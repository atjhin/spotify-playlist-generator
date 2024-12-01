from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Automatically create all tables when the app starts
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
