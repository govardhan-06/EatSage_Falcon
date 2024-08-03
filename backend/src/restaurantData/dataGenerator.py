import json
import random

# Expanded sample data for generating synthetic data
restaurant_names = [
    "Amelie's Cafe & Creamery", "Gourmet Bistro", "The Culinary Haven", "Fusion Feast", "Savory Delights",
    "Bistro Bliss", "Epicurean Eatery", "Culinary Corner", "Taste Paradise", "Gastronomy Galore",
    "Dine Divine", "Flavor Fiesta", "Cuisine Carousel", "Palate Pleasers", "Epic Eats", "Gourmet Grub",
    "Savor Station", "Delectable Dishes", "Feast Finesse", "Taste Treasures", "Fusion Flavors",
    "Gastronomic Garden", "Bistro Bites", "Epicurean Escape", "Savory Stop", "Gourmet Getaway",
    "Culinary Cafe", "Taste Temptations", "Flavor Frenzy", "Palate Paradise", "Epicurean Emporium",
    "Delicious Delights", "Gastronomy Grove", "Bistro Bliss", "Savory Spot", "Gourmet Gathering",
    "Cuisine Kingdom", "Feast Fiesta", "Taste Tavern", "Flavor Fusion", "Culinary Castle", "Epicurean Eatery",
    "Gourmet Garden", "Savory Symphony", "Bistro Bliss", "Gastronomy Grove", "Culinary Carnival",
    "Delicious Diner", "Feast Fest"
]

cuisines = [
    ["Ice Cream", "Italian"], ["French", "Italian"], ["Indian", "Chinese"], ["Mexican", "Italian"], ["Japanese", "Thai"],
    ["American", "BBQ"], ["Mediterranean", "Greek"], ["Vietnamese", "Thai"], ["Lebanese", "Turkish"], ["Korean", "Japanese"],
    ["Italian", "American"], ["Mexican", "French"], ["Greek", "Indian"], ["Chinese", "Mediterranean"], ["Thai", "Japanese"],
    ["Vietnamese", "Korean"], ["American", "BBQ"], ["Lebanese", "Turkish"], ["Vietnamese", "Mediterranean"], ["Indian", "French"]
]

dishes = {
    "Starters": [
        {"name": "Bruschetta", "description": "Grilled bread topped with fresh tomatoes and basil.", "isVeg": True},
        {"name": "Stuffed Mushrooms", "description": "Mushrooms filled with cheese and herbs, baked to perfection.", "isVeg": True},
        {"name": "Chicken Wings", "description": "Spicy and tangy chicken wings.", "isVeg": False},
        {"name": "Spring Rolls", "description": "Crispy rolls filled with vegetables.", "isVeg": True},
        {"name": "Nachos with Cheese", "description": "Crispy nachos topped with melted cheese.", "isVeg": True},
        {"name": "Garlic Bread", "description": "Toasted bread with garlic butter.", "isVeg": True},
        {"name": "Chicken Skewers", "description": "Grilled chicken skewers with a savory marinade.", "isVeg": False},
        {"name": "Veg Pakoras", "description": "Vegetables dipped in chickpea flour batter and fried.", "isVeg": True}
    ],
    "Main Course": [
        {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": True},
        {"name": "Chicken Alfredo Pasta", "description": "Fettuccine pasta tossed in a creamy Alfredo sauce with grilled chicken.", "isVeg": False},
        {"name": "Veg Biryani", "description": "Aromatic rice dish with mixed vegetables and spices.", "isVeg": True},
        {"name": "Grilled Salmon", "description": "Salmon fillet grilled to perfection.", "isVeg": False},
        {"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": False},
        {"name": "Paneer Butter Masala", "description": "Paneer cubes cooked in a rich tomato and cream sauce.", "isVeg": True},
        {"name": "Thai Green Curry", "description": "Spicy green curry with vegetables and basil.", "isVeg": True},
        {"name": "Beef Stroganoff", "description": "Tender beef strips in a creamy mushroom sauce.", "isVeg": False}
    ],
    "Desserts": [
        {"name": "Tiramisu", "description": "Layered dessert with coffee-soaked ladyfingers and mascarpone cheese.", "isVeg": True},
        {"name": "Chocolate Lava Cake", "description": "Warm chocolate cake with a gooey center.", "isVeg": True},
        {"name": "Ice Cream Sundae", "description": "Vanilla ice cream with chocolate syrup and nuts.", "isVeg": True},
        {"name": "Cheesecake", "description": "Creamy cheesecake with a graham cracker crust.", "isVeg": True},
        {"name": "Panna Cotta", "description": "Italian creamy dessert with a vanilla flavor.", "isVeg": True},
        {"name": "Fruit Tart", "description": "Pastry tart filled with custard and topped with fresh fruits.", "isVeg": True},
        {"name": "Brownies", "description": "Rich and fudgy chocolate brownies.", "isVeg": True},
        {"name": "Apple Pie", "description": "Classic apple pie with a flaky crust and spiced apple filling.", "isVeg": True}
    ],
    "Beverages": [
        {"name": "Espresso", "description": "Strong and rich coffee.", "isVeg": True},
        {"name": "Mango Smoothie", "description": "Refreshing smoothie made with fresh mangoes.", "isVeg": True},
        {"name": "Green Tea", "description": "Healthy and soothing green tea.", "isVeg": True},
        {"name": "Lemonade", "description": "Fresh lemonade with a hint of mint.", "isVeg": True},
        {"name": "Cappuccino", "description": "Espresso with steamed milk and foam.", "isVeg": True},
        {"name": "Iced Coffee", "description": "Chilled coffee with a hint of cream.", "isVeg": True},
        {"name": "Herbal Tea", "description": "Caffeine-free herbal tea with calming properties.", "isVeg": True},
        {"name": "Fruit Punch", "description": "Refreshing mix of fruit juices and soda.", "isVeg": True}
    ],
    "Salads": [
        {"name": "Caesar Salad", "description": "Crisp romaine lettuce with Caesar dressing, croutons, and Parmesan.", "isVeg": True},
        {"name": "Greek Salad", "description": "Tomatoes, cucumbers, olives, and feta cheese with Greek dressing.", "isVeg": True},
        {"name": "Quinoa Salad", "description": "Quinoa mixed with vegetables and a tangy vinaigrette.", "isVeg": True},
        {"name": "Caprese Salad", "description": "Sliced tomatoes, mozzarella, and basil with balsamic glaze.", "isVeg": True},
        {"name": "Coleslaw", "description": "Shredded cabbage and carrots with a creamy dressing.", "isVeg": True}
    ],
    "Sandwiches": [
        {"name": "Club Sandwich", "description": "Triple-decker sandwich with chicken, bacon, lettuce, and tomato.", "isVeg": False},
        {"name": "BLT Sandwich", "description": "Bacon, lettuce, and tomato on toasted bread.", "isVeg": False},
        {"name": "Veggie Wrap", "description": "Wrap filled with fresh vegetables and a creamy dressing.", "isVeg": True},
        {"name": "Chicken Panini", "description": "Grilled chicken, cheese, and vegetables pressed in a panini.", "isVeg": False},
        {"name": "Tuna Sandwich", "description": "Tuna salad sandwich with lettuce and tomato.", "isVeg": False}
    ],
    "Pizza": [
        {"name": "Margherita Pizza", "description": "Classic pizza with fresh tomatoes, mozzarella, and basil.", "isVeg": True},
        {"name": "Pepperoni Pizza", "description": "Pizza topped with spicy pepperoni slices.", "isVeg": False},
        {"name": "Veggie Pizza", "description": "Pizza loaded with a variety of vegetables.", "isVeg": True},
        {"name": "BBQ Chicken Pizza", "description": "Pizza with BBQ sauce, grilled chicken, and onions.", "isVeg": False},
        {"name": "Four Cheese Pizza", "description": "Pizza with a blend of four cheeses.", "isVeg": True}
    ],
    "Pasta": [
        {"name": "Spaghetti Carbonara", "description": "Pasta in a creamy carbonara sauce with pancetta and Parmesan.", "isVeg": False},
        {"name": "Penne Arrabbiata", "description": "Penne pasta in a spicy tomato sauce.", "isVeg": True},
        {"name": "Fettuccine Alfredo", "description": "Creamy Alfredo sauce with fettuccine pasta.", "isVeg": True},
        {"name": "Lasagna", "description": "Layered pasta with meat sauce and cheese.", "isVeg": False},
        {"name": "Pesto Pasta", "description": "Pasta tossed with basil pesto sauce.", "isVeg": True}
    ],
    "Burgers": [
        {"name": "Classic Cheeseburger", "description": "Beef patty with cheese, lettuce, and tomato.", "isVeg": False},
        {"name": "Veggie Burger", "description": "Vegetarian patty with lettuce, tomato, and cheese.", "isVeg": True},
        {"name": "BBQ Burger", "description": "Beef patty with BBQ sauce and crispy onions.", "isVeg": False},
        {"name": "Chicken Burger", "description": "Grilled chicken patty with lettuce and mayo.", "isVeg": False},
        {"name": "Bacon Cheeseburger", "description": "Beef patty with bacon, cheese, lettuce, and tomato.", "isVeg": False}
    ]
}

def generate_dishes():
    '''
    Generate a list of dishes based on the given menu categories and ingredients.
    '''
    categories = ["Starters", "Main Course", "Desserts", "Beverages", "Salads", "Sandwiches", "Pizza", "Pasta", "Burgers"]
    category_dishes = {}
    for category in categories:
        dishes_list = random.sample(dishes[category], k=random.randint(1, len(dishes[category])))
        for dish in dishes_list:
            dish['price'] = random.randint(100, 600)
            dish['inStock'] = bool(random.getrandbits(1))
        category_dishes[category] = dishes_list
    return category_dishes

def generate_restaurant_data():
    '''
    Generate restaurant data, including name, location, and menu.
    '''
    name = random.choice(restaurant_names)
    cuisine = random.choice(cuisines)
    area_name = random.choice([
        "Adyar", "Besant Nagar", "T. Nagar", "Anna Nagar", "Nungambakkam", "Kilpauk", "Kodambakkam",
        "Velachery", "Thiruvanmiyur", "Egmore", "Choolaimedu", "Mylapore", "Mount Road", "West Mambalam",
        "Tambaram", "Guindy", "Perungudi", "Perambur", "Sholinganallur", "Saidapet", "Pallikaranai",
        "Kotturpuram", "Koyambedu", "Chromepet", "Vadapalani", "Rajakilpakkam", "Pallavaram", "Nandambakkam",
        "Ashok Nagar", "Srinagar Colony", "Thiruvallur", "Ambattur"
    ])
    locality = random.choice([
        "Mylapore", "T. Nagar", "Adyar", "Anna Nagar", "Besant Nagar", "Nungambakkam", "Kilpauk", "Kodambakkam",
        "Velachery", "Thiruvanmiyur", "Guindy", "Perungudi", "Choolaimedu", "West Mambalam", "Tambaram",
        "Saidapet", "Pallikaranai", "Kotturpuram", "Koyambedu", "Vadapalani", "Rajakilpakkam", "Pallavaram",
        "Nandambakkam", "Ashok Nagar", "Srinagar Colony", "Thiruvallur", "Ambattur", "Mount Road", "Perambur"
    ])
    city = "Chennai"
    rating = round(random.uniform(3.5, 5.0), 1)

    restaurant_data = {
        "data": {
            "About": {
                "Name": name,
                "Ratings": rating,
                "Locality": locality,
                "AreaName": area_name,
                "City": city,
                "Cuisines": cuisine
            },
            "Menu": generate_dishes()
        }
    }
    
    return restaurant_data

if __name__=="__main__":
    restaurant_list = [generate_restaurant_data() for _ in range(50)]

    # Output the data as JSON
    with open('./backend/restaurantData/restaurants.json', 'w') as file:
        json.dump(restaurant_list, file, indent=2)
