from main import SessionLocal, License

db = SessionLocal()

new_license = License(license_key="DALA-1234-TEST")
db.add(new_license)
db.commit()
db.close()

print("License created successfully")