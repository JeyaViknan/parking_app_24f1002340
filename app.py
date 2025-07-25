from flask import Flask, jsonify
from parking.extensions import db, login_manager
from parking.models import ParkingLot, ParkingSpot, Reservation, User
from parking import create_app
from flask_login import current_user, login_required

app = create_app()


# -------- Minimal REST API endpoints -------- #

@app.route("/api/lots", methods=["GET"])
def api_lots():
    lots_data = []
    for lot in ParkingLot.query.all():
        total = len(lot.spots)
        occupied = sum(1 for s in lot.spots if s.status == 'O')
        available = total - occupied
        revenue = (
            db.session.query(db.func.coalesce(db.func.sum(Reservation.total_cost), 0.0))
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
            .filter(ParkingSpot.lot_id == lot.id, Reservation.total_cost.isnot(None))
            .scalar()
        )
        lots_data.append({
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour,
            "address": lot.address,
            "pincode": lot.pincode,
            "max_spots": lot.max_spots,
            "total_spots": total,
            "occupied": occupied,
            "available": available,
            "revenue": float(revenue or 0.0)
        })
    return jsonify(lots_data), 200


@app.route("/api/spots/<int:spot_id>", methods=["GET"])
def api_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    res = {
        "id": spot.id,
        "lot_id": spot.lot_id,
        "status": spot.status,
        "spot_number": spot.spot_number
    }
    active_res = Reservation.query.filter_by(spot_id=spot.id, released_at=None).first()
    if active_res:
        res["occupied_by_user_id"] = active_res.user_id
        res["parked_at"] = active_res.parked_at.isoformat()
    return jsonify(res), 200


@app.route("/api/reservations/me", methods=["GET"])
@login_required
def api_my_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.parked_at.desc()).all()
    data = []
    for r in reservations:
        data.append({
            "id": r.id,
            "spot_id": r.spot_id,
            "lot_id": r.spot.lot_id,
            "parked_at": r.parked_at.isoformat() if r.parked_at else None,
            "released_at": r.released_at.isoformat() if r.released_at else None,
            "total_cost": float(r.total_cost) if r.total_cost is not None else None
        })
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=True)
