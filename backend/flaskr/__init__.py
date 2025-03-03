import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    def paginate_questions(request,selection):
        page = request.args.get('page',1,type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        
        formatted_questions = [question.format() for question in selection]
        current_question = formatted_questions[start:end]
        return current_question

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"   
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            # formatted_categories = [category.format() for category in categories]
            
            if len(categories) == 0:
                abort(404)
                
            return jsonify({
                "success": True,
                # "categories": formatted_categories
                'categories': {category.id: category.type for category in categories}
            })
        except:
            abort(500)
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total_question questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=['GET'])
    def get_questions():
        try:
            categories = Category.query.order_by(Category.id).all()
            formatted_categories = [category.format() for category in categories]    
            categories = Category.query.order_by(Category.type).all()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            
            if len(current_questions) == 0:
                abort(404)
            
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                # "categories": formatted_categories,
                'categories': {category.id: category.type for category in categories},
                "current_category": None
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question is None:
                abort(404)
                
            question.delete()
            
            return jsonify({
                "success": True,
                "deleted": question_id
            })
        except:
            abort(422)    
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions", methods=['POST'])
    def create_question():
        body = request.get_json()
        
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm', None)
        
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                
                current_questions = paginate_questions(request, selection)
                
                if len(current_questions) == 0:
                    abort(404)
                else:
                    return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "current_category": None
                    })
            
            else:
                try:
                    question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
                    question.insert()
                    
                    # selection = Question.query.order_by(Question.id).all()
                    # current_questions = paginate_questions(request, selection)
                    
                    return jsonify({
                        "success": True,
                        "created": question.id,
                    })
                except:
                    abort(400)
        except:
            # print(sys.exc_info())
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions", methods=['GET'])
    def retrieve_category_questions(id):
        try:
            selection = Question.query.filter(Question.category == id).all()
            if len(selection) == 0:
                abort(404)
            current_questions = paginate_questions(request, selection)
            
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "current_category": id
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """


    @app.route('/quizzes', methods=['POST'])
    def generate_quiz_question():
        body = request.get_json()
        try:
            if "previous_questions" and "quiz_category"  not in body:
                abort(400)
                
            previous = body.get("previous_questions")
            category = body.get("quiz_category")

            remaining_questions = Question.query.filter_by(category=category["id"]).filter(Question.id.notin_((previous))).all()

            if len(remaining_questions) >= 1 :
                question = remaining_questions[random.randrange(0, len(remaining_questions))].format() 
                
            else: 
                return None              

            return jsonify({
                "success": True,
                "question": question
            })
        except:
            # print(sys.exc_info())
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found",
        }), 404
        
    @app.errorhandler(422)
    def unproccessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
        
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app

