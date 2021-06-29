# logic for /rating

from searcch_backend.api.app import db, config_name
from searcch_backend.api.common.auth import (verify_api_key, verify_token)
from searcch_backend.models.model import *
from searcch_backend.models.schema import *
from flask import abort, jsonify, request, url_for, Blueprint
from flask_restful import reqparse, Resource, fields, marshal
from sqlalchemy import func, desc, sql


class FavoritesListAPI(Resource):
    @staticmethod
    def generate_artifact_uri(artifact_id):
        return url_for('api.artifact', artifact_id=artifact_id)

    def get(self, user_id):
        verify_api_key(request)
        login_session = verify_token(request)

        if user_id != login_session.user_id:
            abort(401, description="insufficient permission to list favorites")

        sqratings = db.session.query(
            ArtifactRatings.artifact_id,
            func.count(ArtifactRatings.id).label('num_ratings'),
            func.avg(ArtifactRatings.rating).label('avg_rating')
        ).group_by("artifact_id").subquery()
        sqreviews = db.session.query(
            ArtifactReviews.artifact_id,
            func.count(ArtifactReviews.id).label('num_reviews')
        ).group_by("artifact_id").subquery()

        favorite_artifacts = db.session.query(Artifact, 'num_ratings', 'avg_rating', 'num_reviews'
                                                ).join(sqratings, Artifact.id == sqratings.c.artifact_id, isouter=True
                                                ).join(sqreviews, Artifact.id == sqreviews.c.artifact_id, isouter=True
                                                ).join(ArtifactFavorites, Artifact.id == ArtifactFavorites.artifact_id
                                                ).filter(ArtifactFavorites.user_id == login_session.user_id
                                                ).all()

        artifacts = []
        for artifact, num_ratings, avg_rating, num_reviews in favorite_artifacts:
            result = {
                "id": artifact.id,
                "uri": FavoritesListAPI.generate_artifact_uri(artifact.id),
                "doi": artifact.url,
                "type": artifact.type,
                "title": artifact.title,
                "description": artifact.description,                
                "avg_rating": float(avg_rating) if avg_rating else None,
                "num_ratings": num_ratings if num_ratings else 0,
                "num_reviews": num_reviews if num_reviews else 0
            }
            artifacts.append(result)

        response = jsonify({"artifacts": artifacts, "length": len(artifacts)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.status_code = 200
        return response


class FavoriteAPI(Resource):

    def post(self, artifact_id):
        verify_api_key(request)
        login_session = verify_token(request)

        # check for valid artifact id
        artifact = db.session.query(Artifact).filter(
            Artifact.id == artifact_id).first()
        if not artifact:
            abort(400, description='invalid artifact ID')

        # add new rating to the database
        new_favorite = ArtifactFavorites(
            user_id=login_session.user_id, artifact_id=artifact_id)
        db.session.add(new_favorite)
        db.session.commit()

        response = jsonify({"message": "added artifact to favorites list"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.status_code = 200
        return response

    def delete(self, artifact_id):
        verify_api_key(request)
        login_session = verify_token(request)

        existing_favorite = db.session.query(ArtifactFavorites).filter(
            ArtifactFavorites.user_id == login_session.user_id, ArtifactFavorites.artifact_id == artifact_id).first()
        if existing_favorite:
            db.session.delete(existing_favorite)
            db.session.commit()
            response = jsonify(
                {"message": "deleted artifact from favorites list"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.status_code = 200
            return response
        else:
            abort(
                404, description="this artifact does not exist in the user's favorites list")
