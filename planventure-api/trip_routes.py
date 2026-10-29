from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from auth_middleware import login_required
from extensions import db
from flask_jwt_extended import get_jwt_identity
from models import Trip


trips_bp = Blueprint("trips", __name__, url_prefix="/trips")


def parse_date(value, field_name):
    if not isinstance(value, str):
        return None, (jsonify({"error": f"{field_name} is required"}), 400)

    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, (jsonify({"error": f"{field_name} must use YYYY-MM-DD format"}), 400)


def generate_default_itinerary(start_date, end_date):
    itinerary = []
    current_date = start_date
    day_number = 1

    while current_date <= end_date:
        itinerary.append(
            {
                "day": day_number,
                "date": current_date.isoformat(),
                "activities": [],
            }
        )
        current_date += timedelta(days=1)
        day_number += 1

    return itinerary


def serialize_trip(trip):
    return {
        "id": trip.id,
        "user_id": trip.user_id,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "latitude": trip.latitude,
        "longitude": trip.longitude,
        "itinerary": trip.itinerary,
    }


def current_user_trip(trip_id):
    return Trip.query.filter_by(
        id=trip_id,
        user_id=int(get_jwt_identity()),
    ).first()


@trips_bp.route("", methods=["POST"])
@login_required
def create_trip():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400

    destination = data.get("destination")
    if not isinstance(destination, str) or not destination.strip():
        return jsonify({"error": "destination is required"}), 400

    start_date, error = parse_date(data.get("start_date"), "start_date")
    if error:
        return error

    end_date, error = parse_date(data.get("end_date"), "end_date")
    if error:
        return error
    if end_date < start_date:
        return jsonify({"error": "end_date must be on or after start_date"}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    itinerary = data.get("itinerary")

    if latitude is not None and not isinstance(latitude, (int, float)):
        return jsonify({"error": "latitude must be a number"}), 400
    if longitude is not None and not isinstance(longitude, (int, float)):
        return jsonify({"error": "longitude must be a number"}), 400
    if itinerary is not None and not isinstance(itinerary, list):
        return jsonify({"error": "itinerary must be a list"}), 400
    if itinerary is None:
        itinerary = generate_default_itinerary(start_date, end_date)

    trip = Trip(
        user_id=int(get_jwt_identity()),
        destination=destination.strip(),
        start_date=start_date,
        end_date=end_date,
        latitude=latitude,
        longitude=longitude,
        itinerary=itinerary,
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify(serialize_trip(trip)), 201


@trips_bp.route("", methods=["GET"])
@login_required
def list_trips():
    trips = Trip.query.filter_by(user_id=int(get_jwt_identity())).all()
    return jsonify([serialize_trip(trip) for trip in trips])


@trips_bp.route("/<int:trip_id>", methods=["GET"])
@login_required
def get_trip(trip_id):
    trip = current_user_trip(trip_id)
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify(serialize_trip(trip))


@trips_bp.route("/<int:trip_id>", methods=["PUT", "PATCH"])
@login_required
def update_trip(trip_id):
    trip = current_user_trip(trip_id)
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400

    if "destination" in data:
        if not isinstance(data["destination"], str) or not data["destination"].strip():
            return jsonify({"error": "destination is required"}), 400
        trip.destination = data["destination"].strip()

    if "start_date" in data:
        start_date, error = parse_date(data["start_date"], "start_date")
        if error:
            return error
        trip.start_date = start_date

    if "end_date" in data:
        end_date, error = parse_date(data["end_date"], "end_date")
        if error:
            return error
        trip.end_date = end_date

    if trip.end_date < trip.start_date:
        return jsonify({"error": "end_date must be on or after start_date"}), 400

    for field in ("latitude", "longitude"):
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, (int, float)):
                return jsonify({"error": f"{field} must be a number"}), 400
            setattr(trip, field, value)

    if "itinerary" in data:
        if not isinstance(data["itinerary"], list):
            return jsonify({"error": "itinerary must be a list"}), 400
        trip.itinerary = data["itinerary"]

    db.session.commit()
    return jsonify(serialize_trip(trip))


@trips_bp.route("/<int:trip_id>", methods=["DELETE"])
@login_required
def delete_trip(trip_id):
    trip = current_user_trip(trip_id)
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    db.session.delete(trip)
    db.session.commit()
    return jsonify({"message": "Trip deleted successfully"}), 200
