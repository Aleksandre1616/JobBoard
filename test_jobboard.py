import unittest
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from extensions import db
from models import User, Job, Category
from werkzeug.security import generate_password_hash
class JobBoardTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False


        self.app_context = app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        test_user = User(
            name="Test User",
            email="test@example.com",
            password=generate_password_hash("test123")
        )

        db.session.add(test_user)
        db.session.commit()
        second_user = User(
            name="Second User",
            email="second@example.com",
            password=generate_password_hash("second123")
        )

        db.session.add(second_user)
        db.session.commit()

        test_category = Category(
            name="IT"
        )

        db.session.add(test_category)
        db.session.commit()
        test_job = Job(
            title="Second User Job",
            short_description="Test short description",
            description="Test full description",
            company="Test Company",
            salary=1000,
            location="Tbilisi",
            author_id=second_user.id,
            category_id=test_category.id
        )

        db.session.add(test_job)
        db.session.commit()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "test123"
        },
        follow_redirects=True
    )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login successful!", response.data)

    def test_cannot_delete_other_users_job(self):
        self.client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "test123"
            },
            follow_redirects=True
        )

        job = Job.query.filter_by(title="Second User Job").first()

        response = self.client.post(
            f"/job/{job.id}/delete",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"You are not allowed to delete this job.",
            response.data
        )


if __name__ == "__main__":
    unittest.main()