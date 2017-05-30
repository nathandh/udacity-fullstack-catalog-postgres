# udacity-fullstack-catalog
**Catalog App** as part of Udacity's FullStack Nanodegree

The following 'MAIN' files are contained in this project:

* **catalog.py** - The Main ITEM CATALOG implementation file.
	* Uses Flask for routing and API endpoint handling.
	
	* The folloing MAIN App routes are defined:
		1. **`'/'`** OR **`'/catalog/'`**
			* Provides the HOME page routing for the APP
			* Limits ITEMS displayed to last 10 most recent
		2. **`'/full/'`**
			* Route to VIEW all ITEMS in the database
		3. **`'/catalog/category/new/'`**
			* CREATE category endpoint
			* Requires 'admin' role privilege
		4. **`'/catalog/<category>/'`**
			* READ Endpoint for a Single Category
			* Requires 'admin' role privilege
		5. **`'/catalog/<category>/edit/'`**
			* UPDATE category endpoint
			* Requires 'admin' role privilege
		6. **`'/catalog/<category>/delete/'`**
			* DELETE category endpoint
			* Requires 'admin' role privilege
		7. **`'/catalog/<category>/items/'`**
			* View ALL ITEMS for a given Category
		8. **`'/catalog/item/new/'`**
			* CREATE item endpoint
			* Requires 'contrib' role privilege
		9. **`'/catalog/<category>/<item>/'`**
			* READ single ITEM for a given Category
		10. **`'/catalog/<category>/<item>/edit/'`**
			* EDIT Endpoint for Category's Single ITEM
			* Requires 'contrib' role privilege
		11. **`'/catalog/<category>/<item>/delete/'`**
			* DELETE Endpoint for Category's Single ITEM
			* Requires 'contrib' role privilege
		12. **`'/users/'`**
			* View ALL Users stored in the database
		13. **`'/login/'`** OR **`'/catalog/login/'`**
			* App LOGIN endpoint
			* Uses OAuth2 with Google for loggin in
		14. **`'/logout/'`** OR **`'/catalog/logout/'`**
			* App LOGOUT endpoint
			* Disconnects from Google OAuth2

	* API Routing options are as follows:
		1. **`'/catalog.json'`** OR **`'/catalog/categories/json/'`**
			* Outputs JSON for ENTIRE Catalog with Items
		2. **`'/catalog/<category>/json/'`**
			* Outputs a SINGLE Category JSON
		3. **`'/catalog/<category>/items/json/'`**
			* Outputs ALL ITEMS for a given Category in JSON
		4. **`'/items.json'`** OR **`'/catalog/items/json/'`**
			* Outputs JSON for ALL Items in Catalog
		5. **`'/catalog/<category>/<item>/json/'`**
			* Outputs a SINGLE Item JSON
		6. **`'/login-types.json'`** OR **`'/catalog/login-types/json/'`**
			* Output JSON for LoginTypes stored in database
		7. **`'/roles.json'`** OR **`'/catalog/roles/json/'`**
			* Outputs all Roles in JSON
		8. **`'/users.json'`** OR **`'/catalog/users/json/'`**
			* Outputs all Users in JSON

* **database_setup.py** - The DB Schema / Model file.
	* Running the following command creates out 'itemcatalog.db' file:
	```
	python database_setup.py
	```
	* The MAIN model entities defined are as follows:
		1. **LoginType**
			* Login Types for the app
			* Currently: 'google' is the sole type for Google OAuth2 login
		2. **Category**
			* Base Categories for the app
		3. **Item**
			* Category Items for the app
		4. **User**
			* Users of the app
		5. **Role**
			* Roles (e.g. 'admin' or 'contrib' to limit User actions on app

* **test_data.py** - Test data to populate our database initially.
	* Running the following command populates our database with the test data:
	```
	python test_data.py
	```
* **udacity_catalog.sql** - DROP/CREATE SQL for PostgreSQL implementation
	* Run with the following command sequence:
	```
	psql
	\i udacity_catalog.sql
	\q
	```

## Installation:
#### System Requirements:
1. Python 2 (e.g. 2.7.x)
2. Flask libraries
3. SQLAlchemy libraries
4. PostgreSQL (modern version)

#### Obtaining the Code:
* Clone the repository from GitHub
```
git clone https://github.com/nathandh/udacity-fullstack-catalog.git
```

#### Database Setup:
1. Create the Postgres database:
```
cd udacity-fullstack-catalog
psql
\i udacity_catalog.sql
\q
python database_setup.py
```
2. Populate the database with initial Test data
```
python test_data.py 
```

#### Usage:
To run:
1. Ensure 'clients_secrets.json' file exists in top project directory
2. Start the app server instance:
```
python catalog.py
```
3. Visit the app via `http://localhost:9090/` or `http://127.0.0.1:9090`
	* Port 9090 is defined in 'catalog.py' as default port to run app on

#### License:
Licensed for use under the MIT License
