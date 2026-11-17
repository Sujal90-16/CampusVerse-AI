from app.services.security import hash_password, verify_password
def test_password_hash_roundtrip():
 stored=hash_password('CorrectHorseBatteryStaple!')
 assert stored!='CorrectHorseBatteryStaple!'
 assert verify_password('CorrectHorseBatteryStaple!',stored)
 assert not verify_password('wrong-password',stored)
