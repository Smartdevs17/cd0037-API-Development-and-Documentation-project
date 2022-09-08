import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','testpassword','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            "question": "would i have had a good waec if i went to a better school",
            "answer": "the answer all depends as the student is the one that determines whether to succeed or not",
            "difficutly": 4,
            "category": 2
        }
        
        self.wrong_question = {
            "question": "i don't have a good questions",
            "answer": 4,
            "difficulty": "kjdkfajfj"
        }
        
        self.search = {
            "searchTerm": "Peanut butter"
        }
        
        self.wrong_search = {
            "searchTerm": "kdjkfajfda"
        }
        
        self.quiz = {
            'previous_questions': [],
            "quiz_category": {'type': 'Entertainment', 'id': 5}
        }
        
        self.wrong_quiz = {
            'previous_questions': []
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_catogories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertEqual(data["current_category"], None)
        
    def test_404_send_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000",)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    def test_delete_question(self):
        res = self.client().delete("/questions/19")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted"])
    
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete(("/questions/1000"))
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
        
    def test_create_new_question(self):
        res = self.client().post("/questions", json = self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        
    def test_422_create_wrong_question(self):
        res = self.client().post("/questions", json=self.wrong_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    def test_search_question(self):
        res = self.client().post("/questions", json=self.search)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        
    def test_wrong_search_question(self):
        res = self.client().post("/questions", json=self.wrong_search)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    def test_get_questions_of_a_category(self):
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], 5)
        
    def test_get_questions_of_a_category_fails(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
 
      

    def test_quiz_question(self):
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
  
  
    def test_400_quiz_question(self):
        res = self.client().post('/quizzes', json=self.wrong_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")    
          
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()