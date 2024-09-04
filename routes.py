from flask import render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_mail import Message
from datetime import datetime
import os

from extensions import db, mail
from models import Review, Experience, Booking, User
from utils import resize_image, calculate_price_and_season

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/cjena')
    def ueber_uns():
        return render_template('UeberUns.html')

    @app.route('/smjestaj')
    def unterkunft():
        return render_template('Unterkunft.html')

    @app.route('/rezervacija')
    def reservierung():
        return render_template('Reservierung.html')

    @app.route('/erlebnisse')
    def erlebnisse():
        experiences = Experience.query.all()
        return render_template('erlebnisse.html', experiences=experiences)

    @app.route('/rezension')
    def rezension():
        reviews = Review.query.filter_by(confirmed=True).all()
        return render_template('rezension.html', reviews=reviews)

    @app.route('/submit_review', methods=['POST'])
    def submit_review():
        name = request.form['name']
        email = request.form['email']
        rating = request.form['rating']
        review_text = request.form['review']

        new_review = Review(name=name, email=email, rating=rating, review=review_text)
        db.session.add(new_review)
        db.session.commit()

        # E-Mail an den Kunden senden
        customer_msg = Message("Danke für Ihre Bewertung", recipients=[email])
        customer_msg.body = f"""
        Liebe/r {name},

        Vielen Dank für Ihre Bewertung! Wir schätzen Ihr Feedback sehr.

        Ihre Bewertung:
        Sterne: {rating}
        Kommentar: {review_text}

        Mit freundlichen Grüßen,
        Relax Hamulić Team
        """
        mail.send(customer_msg)

        return jsonify({"success": True})

    @app.route('/book', methods=['POST'])
    def book():
        data = request.json
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Überprüfen, ob das Datum bereits gebucht ist
        existing_booking = Booking.query.filter_by(date=booking_date).first()
        if existing_booking:
            return jsonify({"error": "Ovaj datum je već rezervisan"}), 400

        new_booking = Booking(
            date=booking_date,
            name=data['name'],
            email=data['email'],
            time=data['time'],
            persons=data['persons'],
            requests=data.get('requests', '')
        )
        db.session.add(new_booking)
        db.session.commit()

        # Preis und Saison bestimmen
        try:
            price, season = calculate_price_and_season(booking_date, data['persons'])
        except Exception as e:
            app.logger.error(f"Error calculating price and season: {str(e)}")
            return jsonify({"error": "Došlo je do greške prilikom izračuna cijene"}), 500

        # E-Mail an den Kunden
        try:
            customer_msg = Message("Potvrda rezervacije", recipients=[data['email']])
            customer_msg.html = render_template('email/customer_confirmation.html',
                                                name=data['name'],
                                                date=data['date'],
                                                time=data['time'],
                                                persons=data['persons'],
                                                requests=data.get('requests', ''),
                                                price=price,
                                                season=season)
            mail.send(customer_msg)
        except Exception as e:
            app.logger.error(f"Error sending customer email: {str(e)}")
            return jsonify({"error": "Došlo je do greške prilikom slanja e-maila korisniku"}), 500

        # E-Mail an Sie
        try:
            owner_msg = Message("Nova rezervacija", recipients=['nhamulic2003@gmail.com'])
            owner_msg.body = f"""
            Nova rezervacija primljena:
            Ime: {data['name']}
            E-Mail: {data['email']}
            Datum: {data['date']}
            Vrijeme: {data['time']}
            Broj osoba: {data['persons']}
            Posebni zahtjevi: {data.get('requests', '')}
            Cijena: {price} KM
            Sezona: {season}
            """
            mail.send(owner_msg)
        except Exception as e:
            app.logger.error(f"Error sending owner email: {str(e)}")
            return jsonify({"message": "Rezervacija primljena, ali došlo je do greške prilikom slanja e-maila vlasniku"}), 200

        return jsonify({"message": "Rezervacija primljena i e-mailovi poslani"}), 200

    @app.route('/get-booked-dates')
    def get_booked_dates():
        bookings = Booking.query.all()
        booked_dates = [booking.date.strftime('%Y-%m-%d') for booking in bookings]
        return jsonify(booked_dates)

    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            return 'Invalid username or password'
        return render_template('admin_login.html')

    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        bookings = Booking.query.order_by(Booking.date).all()
        return render_template('admin_dashboard.html', bookings=bookings)

    @app.route('/admin/cancel-booking/<int:booking_id>', methods=['POST'])
    @login_required
    def admin_cancel_booking(booking_id):
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/experiences')
    @login_required
    def admin_experiences():
        app.logger.info("Admin experiences route called")
        experiences = Experience.query.all()
        return render_template('admin_experiences.html', experiences=experiences)

    @app.route('/admin/add_experience', methods=['POST'])
    @login_required
    def admin_add_experience():
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            resize_image(image_path)
        new_experience = Experience(title=title, description=description, category=category, image=filename)
        db.session.add(new_experience)
        db.session.commit()
        return redirect(url_for('admin_experiences'))

    @app.route('/admin/delete_experience/<int:experience_id>', methods=['POST'])
    @login_required
    def admin_delete_experience(experience_id):
        experience = Experience.query.get_or_404(experience_id)
        if experience.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], experience.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(experience)
        db.session.commit()
        flash('Erlebnis wurde erfolgreich gelöscht.', 'success')
        return redirect(url_for('admin_experiences'))

    @app.route('/admin/confirm_review/<int:review_id>', methods=['POST'])
    @login_required
    def admin_confirm_review(review_id):
        review = Review.query.get_or_404(review_id)
        review.confirmed = True
        db.session.commit()
        return redirect(url_for('admin_rezensionen'))

    @app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
    @login_required
    def admin_delete_review(review_id):
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        return redirect(url_for('admin_rezensionen'))

    @app.route('/admin/rezensionen')
    @login_required
    def admin_rezensionen():
        reviews = Review.query.all()
        return render_template('admin_rezensionen.html', reviews=reviews)

    