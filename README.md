**RecipeJoy**

RecipeJoy is a PyQt5-based desktop application for managing recipes, ingredients, and nutrition information. It provides a user-friendly interface for adding, editing, and searching recipes, as well as managing food items and custom tags.

**Features**
* Add and edit recipes with ingredients, steps, and nutrition information
* Search recipes by name, calorie range, macronutrients, protein type, or custom tags
* Manage custom tags for recipes
* Add and edit food items with nutrition information
* Calculate and display nutrition information for recipes based on ingredients
* User-friendly interface with intuitive navigation

**Prerequisites**
* Python 3.x
* PyQt5
* pyodbc
* SQL Server Express

**Installation**
1. Clone the repository:
   git clone https://github.com/joywill24/RecipeJoy.git

2. Install the required dependencies:
   pip install PyQt5 pyodbc

3. Set up the database:
   * Install SQL Server Express 2019 or later if you haven't already.
   * During installation, select "Named instance" and use the instance name "SQLEXPRESS".
   * Download the RecipeJoy.bak file from the Assets folder in the GitHub repository.
   * Open SQL Server Management Studio (SSMS) and connect to your local SQLEXPRESS instance.
   * Right-click on "Databases" in the Object Explorer and select "Restore Database...".
   * Choose "Device" as the source, click the "..." button, and select "File" as the backup media.
   * Click "Add" and browse to the location of your downloaded RecipeJoy.bak file.
   * Click "OK" to start the restore process.
  
(Note: If you installed SQL Server Express with a different instance name or if you're 
using a different version of SQL Server, you may need to update the connection string in database.py. 
Look for the following lines and modify the "Server" parameter as needed:

"Driver={SQL Server};"
"Server=localhost\SQLEXPRESS;"
"Database=RecipeJoy;"
"Trusted_Connection=True;")

4. Run the application:
   python main.py

**Usage**
1. Launch the application by running main.py.
   
2. Use the navigation buttons to switch between different sections:
   * Find a Recipe
   * Submit a Recipe
   * Manage Custom Tags
   * Manage Food and Nutrition Info
   * Manage Protein Types

3. Follow the on-screen instructions to add, edit, or search for recipes and food items.

**Project Structure**
* main.py: Entry point of the application
* ui_operations.py: Main UI logic and event handlers
* ui_mainwindow.py: Generated UI code from Qt Designer
* database.py: Database connection management
* recipes_operations.py: Recipe-related database operations
* food_operations.py: Food item-related database operations
* customTags_operations.py: Custom tag-related database operations
* proteins_operations.py: Protein type-related database operations
* custom_dialogs.py: Custom dialog boxes for user interactions
