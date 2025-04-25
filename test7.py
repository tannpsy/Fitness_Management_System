from collections import defaultdict, deque
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import os

class User:
    #Initialize a new instance of the class
    def __init__(self, user_id: str, name: str, age: int, weight: float, height: float):
        # Sets the user_id attribute to the value passed during initialization
        self.user_id = user_id
        # Sets the name attribute
        self.name = name
        # Sets the age attribute
        self.age = age
        # Sets the weight attribute
        self.weight = weight
        # Sets the height attribute
        self.height = height
        # Creates an empty dictionary where keys default to lists for storing activities
        self.activity_log = defaultdict(list)
        # An empty list to store health-related data like BMI or blood pressure
        self.health_metrics = []
        # A deque (double-ended queue) to store the user's last 10 activities
        self.recent_activities = deque(maxlen=10)
        # An empty list to store the user's diet plan information
        self.diet_plan = []
        # An empty list to store the user's workout routines or plans
        self.workout_plan = []
        
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization"""
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        activity_log_dict = {}
        for date, activities in self.activity_log.items():
            date_str = date.isoformat() if isinstance(date, datetime) else str(date)
            activity_log_dict[date_str] = [
                {**activity.__dict__,
                 'timestamp': convert_datetime(activity.timestamp)}
                for activity in activities
            ]

        health_metrics_converted = []
        for metric in self.health_metrics:
            metric_dict = metric.copy()
            if 'timestamp' in metric_dict:
                metric_dict['timestamp'] = convert_datetime(metric_dict['timestamp'])
            health_metrics_converted.append(metric_dict)

        recent_activities_converted = [
            {**activity.__dict__,
             'timestamp': convert_datetime(activity.timestamp)}
            for activity in self.recent_activities
        ]

        return {
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'activity_log': activity_log_dict,
            'health_metrics': health_metrics_converted,
            'recent_activities': recent_activities_converted,
            'diet_plan': [meal.to_dict() for meal in self.diet_plan],
            'workout_plan': [workout.to_dict() for workout in self.workout_plan]
        }

class Activity:
    def __init__(self, activity_type: str, duration: int, calories_burned: float):
        self.activity_type = activity_type
        self.duration = duration
        self.calories_burned = calories_burned
        self.timestamp = datetime.now()
        
    def to_dict(self):
        """Convert activity object to dictionary for JSON serialization"""
        return {
            'activity_type': self.activity_type,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'timestamp': self.timestamp.isoformat()
        }

class Meal:
    def __init__(self, name: str, calories: float, protein: float, carbs: float, fat: float, timestamp: datetime = None):
        self.name = name
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self):
        """Convert meal object to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'timestamp': self.timestamp.isoformat()
        }

class Workout:
    def __init__(self, name: str, difficulty: str, duration: int, calories_burn: float, timestamp: datetime = None):
        self.name = name
        self.difficulty = difficulty
        self.duration = duration
        self.calories_burn = calories_burn
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self):
        """Convert workout object to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'calories_burn': self.calories_burn
        }

class FitnessSystem:
    # Initialize a new instance of the class
    def __init__(self):
        # Create an empty dictionary to store user data
        # Keys could be user IDs, and values could be user details or objects
        self.users = {}
        # Create an empty list to store information about meals
        self.meals_database = []
        # Create an empty list to store workout-related data
        self.workouts_database = []
        # Loads pre-existing user data, meals, or workouts from external files like JSON
        self.load_data()  # Load data from JSON files if they exist
        # Clears the console or terminal screen for a clean user interface when the program starts
        self.clear_screen()
        
    def save_data(self):
        """Save all data to JSON files"""
        users_data = {user_id: user.to_dict() for user_id, user in self.users.items()}
        with open('users.json', 'w') as f:
            json.dump (users_data, f, indent=4)
            
        meals_data = [meal.to_dict() for meal in self.meals_database]
        with open('meals.json', 'w') as f:
            json.dump(meals_data, f, indent=4)
            
        workouts_data = [workout.to_dict() for workout in self.workouts_database]
        with open('workouts.json', 'w') as f:
            json.dump(workouts_data, f, indent=4)
            
    def load_data(self):
        """Load data from JSON files if they exist"""
        try:
            with open('users.json', 'r') as f:
                users_data = json.load(f)
                for user_id, user_data in users_data.items():
                    user = User(
                        user_data['user_id'],
                        user_data['name'],
                        user_data['age'],
                        user_data['weight'],
                        user_data['height']
                    )
                    for date_str, activities in user_data['activity_log'].items():
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        for activity_data in activities:
                            activity = Activity(
                                activity_data['activity_type'],
                                activity_data['duration'],
                                activity_data['calories_burned']
                            )
                            user.activity_log[date].append(activity)
                    user.health_metrics = user_data['health_metrics']
                    user.diet_plan = [Meal(**{**meal, 'timestamp': None}) for meal in user_data['diet_plan']]
                    user.workout_plan = [Workout(**{**workout, 'timestamp': None}) for workout in user_data['workout_plan']]
                    
                    # Restore recent activities
                    for activity_data in user_data['recent_activities']:
                        activity = Activity(
                            activity_data['activity_type'],
                            activity_data['duration'],
                            activity_data['calories_burned']
                        )
                        user.recent_activities.append(activity)
                    
                    self.users[user_id] = user
        except FileNotFoundError:
            pass
            
        try:
            with open('meals.json', 'r') as f:
                meals_data = json.load(f)
                for meal_data in meals_data:
                    meal = Meal(
                        meal_data['name'],
                        meal_data['calories'],
                        meal_data['protein'],
                        meal_data['carbs'],
                        meal_data['fat']
                    )
                    self.meals_database.append(meal)
        except FileNotFoundError:
            pass
            
        try:
            with open('workouts.json', 'r') as f:
                workouts_data = json.load(f)
                for workout_data in workouts_data:
                    workout = Workout(
                        workout_data['name'],
                        workout_data['difficulty'],
                        workout_data['duration'],
                        workout_data['calories_burn']
                    )
                    self.workouts_database.append(workout)
        except FileNotFoundError:
            pass
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def binary_search_user(self, user_id: str) -> bool:
        """Binary search implementation for user lookup"""
        # Get the keys (user IDs) from the self.users dictionary
        # Sort them into a list (sorted_users) for binary search
        sorted_users = sorted(self.users.keys())
        # left: Starts at the beginning of the sorted list (index 0)
        # right: Starts at the end of the sorted list (index len(sorted_users) - 1)
        left, right = 0, len(sorted_users) - 1
        
        # Loop until pointer converge 
        # Repeat the search process while there is still a valid range (left <= right)
        while left <= right:
            # Compute the middle index (mid) of the current range
            mid = (left + right) // 2
            # If the user ID at index mid matches the target user_id, the search is successful
            if sorted_users[mid] == user_id:
                return True
            # Adjust left pointer 
            elif sorted_users[mid] < user_id:
                left = mid + 1
            # Adjust right pointer 
            else:
                right = mid - 1
        return False

    def merge_sort_meals(self, meals: List[Meal]) -> List[Meal]:
        """Merge sort implementation for sorting meals by calories"""
        if len(meals) <= 1:
            return meals
            
        mid = len(meals) // 2
        left = self.merge_sort_meals(meals[:mid])
        right = self.merge_sort_meals(meals[mid:])
        
        return self._merge_meals(left, right)

    def _merge_meals(self, left: List[Meal], right: List[Meal]) -> List[Meal]:
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i].calories <= right[j].calories:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
                
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def quick_sort_workouts(self, workouts: List[Workout]) -> List[Workout]:
        """Quick sort implementation for sorting workouts by calories burn"""
        if len(workouts) <=  1:
            return workouts
            
        pivot = workouts[len(workouts)//2]
        left = [x for x in workouts if x.calories_burn > pivot.calories_burn]
        middle = [x for x in workouts if x.calories_burn == pivot.calories_burn]
        right = [x for x in workouts if x.calories_burn < pivot.calories_burn]
        
        return self.quick_sort_workouts(left) + middle + self.quick_sort_workouts(right)
    
    def greedy_diet_planner(self, target_calories: float) -> List[Meal]:
        """Improved greedy algorithm implementation for meal selection based on calories"""
        # Sorts self.meals_database (list of meals) based on the ratio of calories to protein
        # Meals with higher protein per calorie are prioritized,
        # and meals with zero protein are sorted to the end
        sorted_meals = sorted(self.meals_database, 
                            key=lambda x: (x.calories/x.protein if x.protein > 0 else float('inf')))
        # Creates an empty list to store the selected meals
        recommended_meals = []
        # Starts with zero calories consumed
        current_calories = 0
        # Calculate protein target 
        # Assume 30% of the target calories, divides by 4 because the protein provides 
        # 4 calories per gram 
        protein_target = target_calories * 0.3 / 4  
        # Starts with zero protein consumed
        current_protein = 0
        
        # Loops through the sorted list of meals to select them
        for meal in sorted_meals:
            # Ensures adding the current meal doesn’t exceed the calorie limit
            # Ensures protein consumption is still below the target
            if current_calories + meal.calories <= target_calories and current_protein < protein_target:
                # Adds the meal to the recommended_meals list
                recommended_meals.append(meal)
                # Update calories, add the meal’s calories to current_calories
                current_calories += meal.calories
                # Update protein, add the meal’s protein to current_protein
                current_protein += meal.protein

        # Calculate remaining calories        
        remaining_calories = target_calories - current_calories
        # Check for unallocated calories 
        if remaining_calories > 0:
            # Creates a list of meals not yet added to the recommendations
            remaining_meals = [m for m in sorted_meals if m not in recommended_meals]
            # Sort remaining meals by calorie difference
            for meal in sorted(remaining_meals, key=lambda x: abs(x.calories - remaining_calories)):
                # Allow slight calorie overshoot
                if current_calories + meal.calories <= target_calories * 1.1:  
                    # Adds the meal to the recommended_meals list
                    recommended_meals.append(meal)
                    # Update calories 
                    current_calories += meal.calories
        # Returns the final list of selected meals             
        return recommended_meals

    def dp_workout_scheduler(self, max_duration: int, difficulty: str) -> List[Workout]:
        """Dynamic programming implementation for optimal workout selection"""
        # Filters workouts in self.workouts_database to include only those with the given difficulty level
        suitable_workouts = [w for w in self.workouts_database if w.difficulty == difficulty]
        # Stores the number of filtered workouts in n
        n = len(suitable_workouts)
        
        # Check if workouts exist
        if n == 0:
            # If no suitable workouts are found, return an empty list
            return []
        
        # Initialize DP table
        dp = [[0 for _ in range(max_duration + 1)] for _ in range(n + 1)]
        # Intialize selected table 
        selected = [[False for _ in range(max_duration + 1)] for _ in range(n + 1)]
        
        # Iterate through workouts
        for i in range(1, n + 1):
            # Iterate through duration
            for j in range(1, max_duration + 1):
                # Get the current workout 
                workout = suitable_workouts[i-1]
                # Check if workout fits 
                if workout.duration <= j:
                    # Compare including and excluding the workout
                    if workout.calories_burn + dp[i-1][j-workout.duration] > dp[i-1][j]:
                        # Update DP table (include workout)
                        dp[i][j] = workout.calories_burn + dp[i-1][j-workout.duration]
                        # Mark workout as selected
                        selected[i][j] = True
                    else:
                        # Update DP table (exclude workout)
                        dp[i][j] = dp[i-1][j]
                else:
                    # Skip the workout
                    dp[i][j] = dp[i-1][j]
        #Initialize result list 
        result = []
        # Start backtracking
        i, j = n, max_duration
        # Backtrack through selected table
        while i > 0 and j > 0:
            # Check if workout is included
            if selected[i][j]:
                # Add workout to result 
                result.append(suitable_workouts[i-1])
                # Update remaining duration 
                j -= suitable_workouts[i-1].duration
            # Move to the previous workout 
            i -= 1
        # Return the result 
        return result

    def main_menu(self):
        while True:
            print("\n=== Fitness and Health Management System ===")
            print("1. User Management")
            print("2. Activity Tracking")
            print("3. Diet and Meals")
            print("4. Workout Management")
            print("5. Health Metrics")
            print("6. View Progress")
            print("7. Save and Exit")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                self.user_management_menu()
            elif choice == '2':
                self.activity_menu()
            elif choice == '3':
                self.diet_menu()
            elif choice == '4':
                self.workout_menu()
            elif choice == '5':
                self.health_metrics_menu()
            elif choice == '6':
                self.progress_menu()
            elif choice == '7':
                self.save_data()
                print("\nData saved successfully! Thank you for using the Fitness System!")
                break
            else:
                print("\nInvalid choice. Please try again.")

    def user_management_menu(self):
        while True:
            print("\n=== User Management ===")
            print("1. Add New User")
            print("2. View Users")
            print("3. Delete User")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.add_user_input()
            elif choice == '2':
                self.view_users()
            elif choice == '3':
                self.delete_user_input()
            elif choice == '4':
                break
            else:
                print("\nInvalid choice. Please try again.")

    def add_user_input(self):
        print("\n=== Add New User ===")
        user_id = input("Enter user ID: ")
        if self.binary_search_user(user_id):  # Using binary search
            print("User  ID already exists!")
            return
            
        name = input("Enter name: ")
        age = int(input("Enter age: "))
        weight = float(input("Enter weight (kg): "))
        height = float(input("Enter height (cm): "))
        
        self.users[user_id] = User(user_id, name, age, weight, height)
        print(f"\nUser  {name} added successfully!")

    def view_users(self):
        if not self.users:
            print("\nNo users found in the system.")
            return
            
        print("\n=== Users List ===")
        for user in sorted(self.users.values(), key=lambda x: x.name):
            print(f"\nUser  ID: {user.user_id}")
            print(f"Name: {user.name}")
            print(f"Age: {user.age}")
            print(f"Weight: {user.weight} kg")
            print(f"Height: {user.height} cm")
            print("-" * 30)

    def delete_user_input(self):
        user_id = input("\nEnter user ID to delete: ")
        if self.binary_search_user(user_id):  # Using binary search
            del self.users[user_id]
            print(f"User  {user_id} deleted successfully!")
        else:
            print("User  not found!")

    def recommend_diet_input(self):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):
            print("User  not found!")
            return
            
        target_calories = float(input("Enter daily calorie target: "))
        
        # Using greedy algorithm for meal recommendations
        recommended_meals = self.greedy_diet_planner(target_calories)
        
        if not recommended_meals:
            print("\nNo suitable meals found for your calorie target.")
            return
            
        print("\n=== Recommended Diet Plan ===")
        print(f"Target Calories: {target_calories}")
        total_calories = sum(meal.calories for meal in recommended_meals)
        print(f"Plan Total Calories: {total_calories:.2f}")
        
        print("\nRecommended Meals:")
        for idx, meal in enumerate(recommended_meals, 1):
            print(f"\n{idx}. {meal.name}")
            print(f"   Calories: {meal.calories}")
            print(f"   Protein: {meal.protein}g")
            print(f"   Carbs: {meal.carbs}g")
            print(f"   Fat: {meal.fat}g")
            
        # Save to user's diet plan
        save_plan = input("\nWould you like to save this diet plan? (y/n): ")
        if save_plan.lower() == 'y':
            self.users[user_id].diet_plan = recommended_meals
            print("Diet plan saved successfully!")

    def recommend_workout_input(self):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):
            print("User  not found!")
            return
            
        difficulty = input("Enter preferred difficulty (easy/medium/hard): ").lower()
        max_duration = int(input("Enter maximum workout duration (minutes): "))
        
        # Using dynamic programming for workout recommendations
        recommended_workouts = self.dp_workout_scheduler(max_duration, difficulty)
        
        if not recommended_workouts:
            print("\nNo suitable workouts found for your criteria.")
            return
            
        print("\n=== Recommended Workouts ===")
        total_duration = sum(w.duration for w in recommended_workouts)
        total_calories = sum(w.calories_burn for w in recommended_workouts)
        
        print(f"Total Duration: {total_duration} minutes")
        print(f"Total Calories Burn: {total_calories}")
        
        for idx, workout in enumerate(recommended_workouts, 1):
            print(f"\n{idx}. {workout.name}")
            print(f" Duration: {workout.duration} minutes")
            print(f"   Calories Burn: {workout.calories_burn}")
            print(f"   Difficulty: {workout.difficulty}")
            
        # Save to user's workout plan
        save_plan = input("\nWould you like to save this workout plan? (y/n): ")
        if save_plan.lower() == 'y':
            self.users[user_id].workout_plan = recommended_workouts
            print("Workout plan saved successfully!")

    def activity_menu(self):
        while True:
            print("\n=== Activity Tracking===")
            print("1. Log New Activity")
            print("2. View Activities")
            print("3. Delete Activity")
            print("4. Back to Main Menu")
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.log_activity_input()
            elif choice == '2':
                self.view_activities_input()
            elif choice == '3':
                self.delete_activity_input()
            elif choice == '4':
                break
            else:
                print("\nInvalid choice. Please try again.")

    def log_activity_input(self):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):  # Using binary search
            print("User   not found!")
            return
            
        activity_type = input("Enter activity type (e.g., running, cycling): ")
        duration = int(input("Enter duration (minutes): "))
        calories = float(input("Enter calories burned: "))
        
        activity = Activity(activity_type, duration, calories)
        self.users[user_id].activity_log[datetime.now().date()].append(activity)
        self.users[user_id].recent_activities.append(activity)
        print("\nActivity logged successfully!")

    def view_activities_input(self):
        # Asks the user to input a user id 
        user_id = input("\nEnter user ID: ")
        # Checks if user exist 
        if not self.binary_search_user(user_id):  # Using binary search
            print("User   not found!")
            # Stops further execution if the user does not exist
            return
        
        # Fetches the user object or dictionary associated with the user_id from self.users
        user = self.users[user_id]
        # Verifies if the user’s activity_log is empty
        if not user.activity_log:
            print("\nNo activities found for this user.")
            return # Stops further execution if the activity log is empty
            
        print(f"\n=== Activities for {user.name} ===")
        # Iterate through sorted activity log 
        for date, activities in sorted(user.activity_log.items()):  # Using sorted() for O(n log n)
            print(f"\nDate: {date}")
            # Loops through the list of activities for the current date
            for idx, activity in enumerate(activities, 1):
                print(f"{idx}. {activity.activity_type}")
                print(f"   Duration: {activity.duration} minutes")
                print(f"   Calories: {activity.calories_burned}")
                print(f"   Time: {activity.timestamp.strftime('%H:%M:%S')}")

    def diet_menu(self):
        while True:
            print("\n=== Diet and Meals ===")
            print("1. Add Meal")
            print("2. View Meals")
            print("3. Delete Meal")
            print("4. Get Diet Recommendations")
            print("5. View Saved Plans")
            print("6. Delete Saved Diet Plan")
            print("7. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                self.add_meal_input()
            elif choice == '2':
                self.view_meals()
            elif choice == '3':
                self.delete_meal_input()
            elif choice == '4':
                self.recommend_diet_input()
            elif choice == '5':
                self.view_saved_plans('diet')
            elif choice == '6':
                self.delete_saved_plan_input('diet')
            elif choice == '7':
                break
            else:
                print("\nInvalid choice. Please try again.")
                
    def workout_menu(self):
        while True:
            print("\n=== Workout Management ===")
            print("1. Add Workout")
            print("2. View Workouts")
            print("3. Delete Workout")
            print("4. Get Workout Recommendations")
            print("5. View Saved Plans")
            print("6. Delete Saved Workout Plan")
            print("7. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                self.add_workout_input()
            elif choice == '2':
                self.view_workouts()
            elif choice == '3':
                self.delete_workout_input()
            elif choice == '4':
                self.recommend_workout_input()
            elif choice == '5':
                self.view_saved_plans('workout')
            elif choice == '6':
                self.delete_saved_plan_input('workout')
            elif choice == '7':
                break
            else:
                print("\nInvalid choice. Please try again.")

    def add_workout_input(self):
        name = input("\nEnter workout name: ")
        difficulty = input("Enter difficulty (easy/medium/hard): ")
        duration = int(input("Enter duration (minutes): "))
        calories = float(input("Enter estimated calories burn: "))
        
        workout = Workout(name, difficulty, duration, calories)
        self.workouts_database.append(workout)
        print("\nWorkout added successfully!")

    def view_workouts(self):
        if not self.workouts_database:
            print("\nNo workouts in database.")
            return
        sorted_workouts = self.quick_sort_workouts(self.workouts_database.copy())
        print("\n=== Workouts Database ===")
        for idx, workout in enumerate(sorted_workouts, 1):
            print(f"\n{idx}. {workout.name}")
            print(f"   Difficulty: {workout.difficulty}")
            print(f"   Duration: {workout.duration} minutes")
            print(f"   Calories Burn: {workout.calories_burn}")

    def add_meal_input(self):
        name = input("\nEnter meal name: ")
        calories = float(input("Enter calories: "))
        protein = float(input("Enter protein (g): "))
        carbs = float(input("Enter carbs (g): "))
        fat = float(input("Enter fat (g): "))
        
        meal = Meal(name, calories, protein, carbs, fat)
        self.meals_database.append(meal)
        print("\nMeal added successfully!")

    def view_meals(self):
        if not self.meals_database:
            print("\nNo meals in database.")
            return
            
        # Using Merge Sort for sorted display
        sorted_meals = self.merge_sort_meals(self.meals_database.copy())
        print("\n=== Meals Database ===")
        for idx, meal in enumerate(sorted_meals, 1):
            print(f"\n{idx}. {meal.name}")
            print(f"   Calories: {meal.calories}")
            print(f"   Protein: {meal.protein}g")
            print(f"   Carbs: {meal.carbs}g")
            print(f"   Fat: {meal.fat}g")

    def log_health_metric_input(self):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):  # Using binary search
            print("User   not found!")
            return
            
        metric_type = input("Enter metric type (heart_rate/blood_pressure/weight): ")
        value = float(input("Enter value: "))
        
        metric = {"type": metric_type, "value": value, "timestamp": datetime.now()}
        self.users[user_id].health_metrics.append(metric)
        print("\nHealth metric logged successfully!")

    def view_health_metrics_input(self):
        # Asks the user to input a user ID
        user_id = input("\nEnter user ID: ")
        # Check if the user exist 
        if not self.binary_search_user(user_id): # Uses binary search 
            print("User   not found!")
            # Stops execution if the user does not exist
            return

        # Fetches the user object corresponding to the given user ID
        user = self.users[user_id]
        # Verifies if the user has any recorded health metrics
        if not user.health_metrics:
            print("\nNo health metrics recorded for this user.")
            return

        print(f"\n=== Health Metrics for {user.name} ===")
        # Loops through each health metric in the user's health_metrics list
        for metric in user.health_metrics:
            # Convert timestamp to datetime if needed
            if isinstance(metric['timestamp'], str):
                metric['timestamp'] = datetime.fromisoformat(metric['timestamp'])
            print(f"\nType: {metric['type']}")
            print(f"Value: {metric['value']}")
            print(f"Time: {metric['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

    def delete_activity_input(self):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):  # Using binary search
            print("User   not found!")
            return
            
        user = self.users[user_id]
        if not user.activity_log:
            print("\nNo activities found for this user.")
            return
            
        print("\nAvailable activities:")
        activities_list = []
        for date, activities in sorted(user.activity_log.items()):  # Using sorted() for O(n log n)
            for activity in activities:
                activities_list.append((date, activity))
                idx = len(activities_list)
                print(f"{idx}. {activity.activity_type} on {date} - {activity.duration} minutes")
        
        try:
            choice = int(input("\nEnter number of activity to delete (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(activities_list):
                date, _ = activities_list[choice-1]
                user.activity_log[date].pop(choice-1)
                if not user.activity_log[date]:
                    del user.activity_log[date]
                print("\nActivity deleted successfully!")
            else:
                print("\nInvalid choice!")
        except ValueError:
            print("\nInvalid input!")

    def delete_meal_input(self):
        if not self.meals_database:
            print("\nNo meals in database.")
            return
            
        print("\nAvailable meals:")
        for idx, meal in enumerate(self.meals_database, 1):
            print(f"{idx}. {meal.name}")
        
        try:
            choice = int(input("\nEnter number of meal to delete (0 to cancel): "))
            if choice == 0:
                return
            if  1 <= choice <= len(self.meals_database):
                deleted_meal = self.meals_database.pop(choice-1)
                print(f"\nMeal '{deleted_meal.name}' deleted successfully!")
            else:
                print("\nInvalid choice!")
        except ValueError:
            print("\nInvalid input!")

    def delete_workout_input(self):
        if not self.workouts_database:
            print("\nNo workouts in database.")
            return
            
        print("\nAvailable workouts:")
        for idx, workout in enumerate(self.workouts_database, 1):
            print(f"{idx}. {workout.name}")
        
        try:
            choice = int(input("\nEnter number of workout to delete (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(self.workouts_database):
                deleted_workout = self.workouts_database.pop(choice-1)
                print(f"\nWorkout '{deleted_workout.name}' deleted successfully!")
            else:
                print("\nInvalid choice!")
        except ValueError:
            print("\nInvalid input!")

    def health_metrics_menu(self):
        while True:
            print("\n=== Health Metrics ===")
            print("1. Log Health Metric")
            print("2. View Health Metrics")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == '1':
                self.log_health_metric_input()
            elif choice == '2':
                self.view_health_metrics_input()
            elif choice == '3':
                break
            else:
                print("\nInvalid choice. Please try again.")

    def progress_menu(self):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):  # Using binary search
            print("User    not found!")
            return
            
        days = int(input("Enter number of days for progress report: "))
        
        user = self.users[user_id]
        progress = self.calculate_progress(user_id, days)
        
        print(f"\n=== Progress Report for {user.name} ===")
        print(f"Period: Last {days} days")
        print(f"\nTotal Activities: {progress['total_activities']}")
        print(f"Total Calories Burned: {progress['total_calories']:.2f}")
        print(f"Average Daily Activities: {progress['avg_daily_activities']:.2f}")
        print(f"Average Daily Calories: {progress['avg_daily_calories']:.2f}")

    def calculate_progress(self, user_id: str, days: int) -> Dict[str, float]:
        """Calculate progress using sliding window algorithm - O(n)"""
        # Fetches the user object associated with the given user_id
        user = self.users[user_id]
        # Sets the end date to the current date
        end_date = datetime.now().date()
        # Determines the start date by subtracting the specified number of days from the end date
        start_date = end_date - timedelta(days=days)
        
        # Creates a variable to count the total number of activities
        total_activities = 0
        # Creates a variable to sum the total calories burned
        total_calories = 0
        
        # Set current date 
        current_date = start_date
        # Loops through each day from start_date to end_date
        while current_date <= end_date:
            # Verifies if the user has activity logs for the current date
            if current_date in user.activity_log:
                # Update activity count 
                total_activities += len(user.activity_log[current_date])
                # Update calorie count 
                total_calories += sum(activity.calories_burned for activity in user.activity_log[current_date])
            #Move to the next date 
            current_date += timedelta(days=1)
        
        # Creates and returns a dictionary containing progress metrics
        return {
            # Includes the total number of activities in the result
            'total_activities': total_activities,
            # Includes the total calories burned in the result
            'total_calories': total_calories,
            # alculates and includes the average number of daily activities
            'avg_daily_activities': total_activities / days if days > 0 else 0,
            # Calculates and includes the average calories burned per day
            'avg_daily_calories': total_calories / days if days > 0 else 0
        }

    def view_saved_plans(self, plan_type: str):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):  # Using binary search
            print("User    not found!")
            return
            
        user = self.users[user_id]
        if plan_type == 'diet':
            if not user.diet_plan:
                print("\nNo saved diet plan found for this user.")
                return
            print("\n=== Saved Diet Plan ===")
            for idx, meal in enumerate(user.diet_plan, 1):
                print(f"\n{idx}. {meal.name}")
                print(f"   Calories: {meal.calories}")
                print(f"   Protein: {meal.protein}g")
                print(f"   Carbs: {meal.carbs}g")
                print(f"   Fat: {meal.fat}g")
        elif plan_type == 'workout':
            if not user.workout_plan:
                print("\nNo saved workout plan found for this user.")
                return
            print("\n=== Saved Workout Plan ===")
            for idx, workout in enumerate(user.workout_plan, 1):
                print(f"\n{idx}. {workout.name}")
                print(f"   Duration: {workout.duration} minutes")
                print(f"   Calories Burn: {workout.calories_burn}")
                print(f"   Difficulty: {workout.difficulty}")

    def delete_saved_plan_input(self, plan_type: str):
        user_id = input("\nEnter user ID: ")
        if not self.binary_search_user(user_id):  # Using binary search
            print("User    not found!")
            return
            
        user = self.users[user_id]
        if plan_type == 'diet':
            user.diet_plan = []
            print("Diet plan deleted successfully!")
        elif plan_type == 'workout':
            user.workout_plan = []
            print("Workout plan deleted successfully!")

def main():
    system = FitnessSystem()
    system.main_menu()

if __name__ == "__main__":
    main()