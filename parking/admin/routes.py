from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from parking.extensions import db
from parking.models import ParkingLot, ParkingSpot, Reservation, User
from .forms import ParkingLotForm

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


def admin_required(func_):
    from functools import wraps

    @wraps(func_)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return func_(*args, **kwargs)

    return wrapper


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    lots = ParkingLot.query.all()
    users = User.query.all()

    # Occupancy & revenue data for charts
    occupancy_labels = []
    occupied_data = []
    available_data = []
    revenue_labels = []
    revenue_data = []

    for lot in lots:
        total = len(lot.spots)
        occupied = sum(1 for s in lot.spots if s.status == 'O')
        available = total - occupied
        occupancy_labels.append(lot.prime_location_name)
        occupied_data.append(occupied)
        available_data.append(available)

        revenue = (
            db.session.query(func.coalesce(func.sum(Reservation.total_cost), 0.0))
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
            .filter(ParkingSpot.lot_id == lot.id, Reservation.total_cost.isnot(None))
            .scalar()
        )
        revenue_labels.append(lot.prime_location_name)
        revenue_data.append(float(revenue or 0.0))

    q_spot_id = request.args.get("spot_id", type=int)
    searched_spot = None
    active_reservation = None
    if q_spot_id:
        searched_spot = ParkingSpot.query.get(q_spot_id)
        if searched_spot:
            active_reservation = Reservation.query.filter_by(spot_id=searched_spot.id, released_at=None).first()

    return render_template(
        "admin/dashboard.html",
        lots=lots,
        users=users,
        occupancy_labels=occupancy_labels,
        occupied_data=occupied_data,
        available_data=available_data,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data,
        searched_spot=searched_spot,
        active_reservation=active_reservation
    )


@admin_bp.route("/lots/new", methods=["GET", "POST"])
@login_required
@admin_required
def lot_create():
    form = ParkingLotForm()
    if form.validate_on_submit():
        lot = ParkingLot(
            prime_location_name=form.prime_location_name.data.strip(),
            price_per_hour=form.price_per_hour.data,
            address=form.address.data.strip(),
            pincode=form.pincode.data.strip(),
            max_spots=form.max_spots.data
        )
        db.session.add(lot)
        db.session.flush()  # get lot.id

        # Auto-generate spots
        for i in range(1, lot.max_spots + 1):
            spot = ParkingSpot(lot_id=lot.id, status='A', spot_number=i)
            db.session.add(spot)

        db.session.commit()
        flash("Parking lot created successfully with spots generated.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/lot_form.html", form=form, action="Create")


@admin_bp.route("/lots/<int:lot_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def lot_edit(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    form = ParkingLotForm(obj=lot)
    if form.validate_on_submit():
        lot.prime_location_name = form.prime_location_name.data.strip()
        lot.price_per_hour = form.price_per_hour.data
        lot.address = form.address.data.strip()
        lot.pincode = form.pincode.data.strip()
        new_max_spots = form.max_spots.data

        if new_max_spots < lot.max_spots:
            flash("Reducing spots is not supported in V1.", "warning")
        else:
            # Add additional spots if increased
            for i in range(lot.max_spots + 1, new_max_spots + 1):
                db.session.add(ParkingSpot(lot_id=lot.id, status='A', spot_number=i))
            lot.max_spots = new_max_spots

        db.session.commit()
        flash("Parking lot updated.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/lot_form.html", form=form, action="Edit")


@admin_bp.route("/lots/<int:lot_id>/delete", methods=["POST"])
@login_required
@admin_required
def lot_delete(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    # Check any occupied spots
    occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occupied > 0:
        flash("Cannot delete lot with occupied spots.", "danger")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted.", "success")
    return redirect(url_for("admin.dashboard"))
