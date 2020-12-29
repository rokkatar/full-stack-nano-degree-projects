import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/": {'origins':'*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
    return response

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    print("PAGE", page)
    start = (page - 1) * QUESTIONS_PER_PAGE
    print("START", start)
    end = start + QUESTIONS_PER_PAGE
    print("END", end)
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    if (len(current_questions) == 0):
      abort(404)
    return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    # GET all questions and paginate, abort if no questions
    selection = Question.query.order_by(Question.id).all()
    paginated_questions = paginate_questions(request, selection)
    if len(paginated_questions) == 0:
      abort(404)

    # GET all categories and format into a list of dicts
    category_query = Category.query.all()
    all_categories = [cat.format() for cat in category_query]
    #print(all_categories)
    category_names = []
    for cat in all_categories:
      category_names.append(cat['type'])
    #print(category_names)
    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(selection),
      'categories': category_names,
      'current_category': category_names
      })

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def get_categories():
    if(request.method != 'GET'):
      abort(405)
    selection = Category.query.order_by(Category.id).all()
    if not selection:
      abort(404)
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in selection}
                   })
  
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    selection = Question.query.filter(Question.id == question_id).one_or_none()
    if not selection:
      abort(400)
    try:
      selection.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    if not body:
      abort(400)

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    if not new_question:
      abort(400)
    if not new_answer:
      abort(400)
    if not new_category:
      abort(400)
    if not new_difficulty:
      abort(400)

    try:
      new_trivia = Question(
        question = new_question,
        answer = new_answer,
        category = new_category,
        difficulty = new_difficulty
      )
      new_trivia.insert()
      selection = Question.query.order_by(Question.id).all()
      paginated_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'qid': new_trivia.id,
        'questions': paginated_questions,
        'total_questions': len(selection)
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    if not body:
      abort(400)
    search_term = body.get('searchTerm', None)
    if not search_term:
      abort(400)
    try:
      search_results = Question.query.filter(Question.question.contains(search_term)).all()
      paginated_questions = paginate_questions(request, search_results)
      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': len(search_results),
        'current_category': 'TBC'
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    # GET all questions and paginate, abort if no questions
    selection = Question.query.filter(Question.category == str(category_id)).all()
    if len(selection) == 0:
      abort(400)
    paginated_questions = paginate_questions(request, selection)
    # GET all categories and format into a list of dicts
    category_query = Category.query.all()
    all_categories = [cat.format() for cat in category_query]

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(selection),
      'categories': all_categories,
      'current_category': 'TBC'
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def post_play_quiz():
    # Return a question from selected category
    body = request.get_json()
    if not body:
      abort(400)
    previous_questions = body.get('previous_questions', None)
    print("PREVIOUS QUESTIONS: ", previous_questions)
    current_category = body.get('quiz_category', None)

    # if no questions...
    if not previous_questions:
      #print("not previous_questions")
      # then either select questions from category...
      if current_category:
        #print("current_category")
        quiz_questions = (Question.query
          .filter(Question.category == str(current_category['id']))
          .all())
        if not quiz_questions:
          #print("not quiz_questions")
          quiz_questions = Question.query.all()
      # or just select all questions
      else:
        #print("else select all")
        quiz_questions = Question.query.all()

    # if previous questions, exclude them from selection
    else:
      #if previous questions and a category
      if current_category:
        #print("previous questions and current category")
        quiz_questions = (Question.query
          .filter(Question.category == str(current_category['id']))
          .filter(Question.id.notin_(previous_questions))
          .all())
      #if previous questions, but no category
      if not quiz_questions:
        #print("previous questions and no category")
        quiz_questions = (Question.query
          .filter(Question.id.notin_(previous_questions))
          .all())

    #print(quiz_questions)
    quiz_questions_formatted = [question.format() for question in quiz_questions]
    #print(quiz_questions_formatted)
    question_number = random.randint(0, (len(quiz_questions_formatted)-1))
    #print(question_number)
    quiz_question_rand = quiz_questions_formatted[question_number]
    
    return jsonify({
        'success': True,
        'question': quiz_question_rand
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
#----------------------------------------------------------------------------#
# API error handlers
#----------------------------------------------------------------------------#
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      "message": "bad request"
    }), 400
  
  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable entity'
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'internal server error'
    }), 422
    

  return app
    