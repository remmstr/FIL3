# Requirements modules
import bcrypt

class Credentials():
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, value: str):
        self._username = value

    @property
    def password(self) -> bytes:
        """Return the password in hashed form."""
        return self._password
    
    @password.setter
    def password(self, value: str):
        self._password = bcrypt.hashpw(value.encode(), bcrypt.gensalt())

    def check_password(self, password: str):
        """Check hashed password. Using bcrypt, the salt is saved into the hash itself."""
        return bcrypt.checkpw(password.encode(), self.password)

if __name__ == '__main__':
    test_cred = Credentials("MyMan", "321ftw")

    print("USERNAME: {}".format(test_cred.username))
    print("PASSWORD: {}".format(test_cred.password), end="\n\n")

    print(test_cred.check_password("321ftw")) # Send True
    print(test_cred.check_password("wtf123")) # Send False

    test_cred.password = "wtf123"

    print(test_cred.check_password("wtf123")) # Send True