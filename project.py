from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import json
from gtts import gTTS
import os

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def showLanding():
	return render_template('landing.html')

@app.route('/restaurants/')
def showRestaurants():
	#restaurants = session.query(Restaurant).order_by(Restaurant.name).all()
	with open('table1.json') as f:
		d = json.load(f)
	restaurants = d
	print(restaurants)
	return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurant/new/', methods = ['GET', 'POST'])
def newRestaurant():
	if request.method =='POST':
		restaurant = Restaurant(name = request.form['name'])
		session.add(restaurant)
		session.commit()

		flash('New restaurant %s created!' % restaurant.name)
		return redirect(url_for('showRestaurants'))

	else:
		return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		restaurant.name = request.form['name']
		session.add(restaurant)
		session.commit()
		flash("Restaurant name updated.")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editRestaurant.html', restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		flash("Restaurant deleted.")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleteRestaurant.html', restaurant = restaurant)


@app.route('/restaurant/<string:restaurant_name>/menu')
@app.route('/restaurant/<string:restaurant_name>/')
def showMenu(restaurant_name):
	#restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	#items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
	restaurants = []
	voiceOverList = []
	with open('table2.json') as f:
		d = json.load(f)

	for i in range(len(d)):
		if d[i]['name'] == restaurant_name:
			restaurants.append(d[i].copy())
	# 		voiceOverList.append(d[i]['dishName'])
	# 		voiceOverList.append(d[i]['dishPrice'])
	# #print(voiceOverList)
	# for i in range(len(voiceOverList)):
	# 	tts = gTTS(text=voiceOverList[i], lang='en')
	# 	tts.save("good.mp3")
	# 	os.system("mpg321 good.mp3")
	#
	#
	#
	# for i in range(voiceOverList):
	#
	# 	tts = gTTS(text=voiceOverList[i], lang='en')
	# 	tts.save("good.mp3")
	# 	os.system("mpg321 good.mp3")
	#
	# print(restaurants)
	return render_template('menu.html', restaurants = restaurants, restaurant_name = restaurant_name)




@app.route('/restaurants/json')
def retaurantsJson():
    restaurant = session.query(Restaurant).all()
    return jsonify(MenuItems= [r.serialize for r in restaurant])

@app.route('/restaurant/<int:restaurant_id>/menu/json')
def retaurantMenuJson(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return jsonify(MenuItems= [i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/json')
def retaurantMenuItemJson(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItems= item.serialize)


if __name__ == '__main__':
	app.secret_key = "my_secret_key"
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
