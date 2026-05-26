import db
from flask import redirect

def get_recipes():
    sql = """SELECT id, title, date, status
             FROM recipes
             ORDER BY id DESC"""
    
    return db.query(sql)

def get_recipe(recipe_id):
    sql = """SELECT id, title, ingredients, instructions, status
             FROM recipes 
             WHERE id = ?"""
    
    return db.query(sql, [recipe_id])[0]

def update_recipe(recipe_id, title, ingredients, instructions):
    sql = """UPDATE recipes
             SET title = ?,
                 ingredients = ?,
                 instructions = ?
             WHERE id = ?;"""
    
    db.execute(sql, [title, ingredients, instructions, recipe_id])

def delete_recipe(recipe_id):
    sql = """UPDATE recipes
             SET status = 0
             WHERE id = ?"""
    
    db.execute(sql, [recipe_id])