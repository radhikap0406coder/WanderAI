"""
Rich destination database with real coordinates, attractions, local dining, 
cultural tips, and financial heuristics for popular global spots and multi-city regions.
"""
import re
from typing import Dict, Any, List, Optional

DESTINATIONS_DATA = {
    "tokyo": {
        "name": "Tokyo, Japan",
        "country": "Japan",
        "tagline": "Neon Metropolises, Ancient Shrines & Culinary Perfection",
        "description": "A dazzling blend of futuristic technology and centuries-old traditions.",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [35.6762, 139.6503],
        "climate": "Moderate temperate climate. Cherry blossoms in Spring (March-April), crisp Fall (Oct-Nov).",
        "recommended_duration": 6,
        "currency": "JPY",
        "cost_tier": "Moderate to High",
        "popular_interests": ["Culinary & Dining", "Culture & History", "Shopping", "Futuristic Tech"],
        "customs": [
            "Bow politely when greeting and never leave chopsticks standing upright in rice.",
            "Tipping is not customary and can cause confusion; excellent service is included.",
            "Keep voice quiet on public trains and subways; refrain from phone calls.",
            "Carry a small bag for your trash as public garbage bins are rare."
        ],
        "emergency": {"police": "110", "ambulance": "119", "helpline": "+81-3-5777-8600"},
        "spots": [
            {"name": "Senso-ji Temple & Asakusa", "city": "Tokyo", "lat": 35.7148, "lng": 139.7967, "category": "Culture", "cost": 0, "best_time": "Morning (08:30 - 11:30)", "desc": "Tokyo's oldest and most significant Buddhist temple with vibrant Nakamise shopping street."},
            {"name": "Meiji Jingu Shrine & Harajuku", "city": "Tokyo", "lat": 35.6764, "lng": 139.6993, "category": "Culture", "cost": 0, "best_time": "Morning (09:00 - 12:00)", "desc": "Serene forest shrine dedicated to Emperor Meiji, juxtaposed beside colorful Takeshita Street."},
            {"name": "Shibuya Crossing & Hachiko Statue", "city": "Tokyo", "lat": 35.6595, "lng": 139.7005, "category": "Sightseeing", "cost": 0, "best_time": "Evening (17:00 - 19:30)", "desc": "The world's busiest pedestrian scramble, breathtaking neon billboards, and iconic Shibuya Sky deck."},
            {"name": "Tsukiji Outer Market Tasting Tour", "city": "Tokyo", "lat": 35.6655, "lng": 139.7708, "category": "Dining", "cost": 35, "best_time": "Morning (08:30 - 11:00)", "desc": "Feast on fresh sushi rolls, tamagoyaki, wagyu skewers, and matcha sweets directly from artisanal vendors."},
            {"name": "Akihabara Electric Town", "city": "Tokyo", "lat": 35.6983, "lng": 139.7731, "category": "Sightseeing", "cost": 20, "best_time": "Afternoon (14:00 - 17:00)", "desc": "The global hub of anime, gaming arcades, retro electronics, and quirky concept cafes."},
            {"name": "Shinjuku Gyoen National Garden", "city": "Tokyo", "lat": 35.6852, "lng": 139.7101, "category": "Nature", "cost": 5, "best_time": "Afternoon (13:00 - 15:30)", "desc": "Sprawling imperial park blending traditional Japanese gardens with French formal and English landscape design."},
            {"name": "teamLab Planets Digital Art Museum", "city": "Tokyo", "lat": 35.6491, "lng": 139.7898, "category": "Attraction", "cost": 38, "best_time": "Afternoon (15:00 - 17:30)", "desc": "Immersive water and mirror infinity exhibits where visitors walk barefoot through living digital light art."},
            {"name": "Omoide Yokocho & Golden Gai", "city": "Tokyo", "lat": 35.6928, "lng": 139.7001, "category": "Dining", "cost": 45, "best_time": "Evening (19:00 - 22:00)", "desc": "Intimate lantern-lit alleyways packed with sizzling yakitori grills and cozy 6-seat izakayas."},
            {"name": "Ginza Shopping & Kabuki-za Theater", "city": "Tokyo", "lat": 35.6719, "lng": 139.7650, "category": "Shopping", "cost": 25, "best_time": "Afternoon (14:00 - 17:00)", "desc": "Tokyo's premier high-end district with flagship architectural marvels and theaters."},
            {"name": "Roppongi Hills Mori Art Museum View", "city": "Tokyo", "lat": 35.6605, "lng": 139.7292, "category": "Attraction", "cost": 22, "best_time": "Evening (18:30 - 21:00)", "desc": "52nd-floor 360-degree observation deck with panoramic views of Tokyo Tower and Mt. Fuji silhouette."}
        ]
    },
    "paris": {
        "name": "Paris, France",
        "country": "France",
        "tagline": "The City of Light, Haute Cuisine & Timeless Romance",
        "description": "Grand boulevards, world-class art institutions, bistro terraces, and iconic riverbanks.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [48.8566, 2.3522],
        "climate": "Mild European climate. Glorious spring flowers in May; golden autumn leaves in October.",
        "recommended_duration": 5,
        "currency": "EUR",
        "cost_tier": "High",
        "popular_interests": ["Art & History", "Culinary & Wine", "Romance", "Architecture"],
        "customs": [
            "Always greet shopkeepers and waiters with 'Bonjour Madame/Monsieur' before asking questions.",
            "Take your time at meals; rushing dinner is considered unrefined.",
            "Tipping around 5-10% is appreciated for good service, though 'service compris' is included."
        ],
        "emergency": {"police": "17", "ambulance": "15", "general_emergency": "112"},
        "spots": [
            {"name": "Eiffel Tower & Champ de Mars", "city": "Paris", "lat": 48.8584, "lng": 2.2945, "category": "Sightseeing", "cost": 29, "best_time": "Evening (18:30 - 21:30)", "desc": "Ascend the iron lady for golden hour vistas and witness the mesmerizing hourly sparkle at dusk."},
            {"name": "The Louvre Museum & Cour Napoléon", "city": "Paris", "lat": 48.8606, "lng": 2.3376, "category": "Culture", "cost": 22, "best_time": "Morning (09:00 - 12:30)", "desc": "Home to the Mona Lisa, Venus de Milo, and over 35,000 masterpieces within the former royal palace."},
            {"name": "Montmartre & Sacré-Cœur Basilica", "city": "Paris", "lat": 48.8867, "lng": 2.3431, "category": "Culture", "cost": 0, "best_time": "Morning (09:30 - 12:00)", "desc": "Bohemian hilltop quarter filled with street portrait artists, cobblestone alleys, and sweeping panoramas."},
            {"name": "Seine River Sunset Cruise", "city": "Paris", "lat": 48.8599, "lng": 2.2965, "category": "Attraction", "cost": 18, "best_time": "Evening (19:30 - 21:00)", "desc": "Glide under historic stone bridges past illuminated Notre-Dame, Musée d'Orsay, and the Grand Palais."},
            {"name": "Musée d'Orsay & French Impressionism", "city": "Paris", "lat": 48.8600, "lng": 2.3266, "category": "Culture", "cost": 16, "best_time": "Afternoon (13:30 - 16:30)", "desc": "Breathtaking converted railway terminal exhibiting Monet, Van Gogh, Degas, and Renoir."},
            {"name": "Le Marais Historic Walk & Falafel Lunch", "city": "Paris", "lat": 48.8575, "lng": 2.3622, "category": "Dining", "cost": 24, "best_time": "Afternoon (12:00 - 15:00)", "desc": "Aristocratic 17th-century mansions, fashionable boutiques, Place des Vosges, and legendary eats."},
            {"name": "Sainte-Chapelle Stained Glass Marvel", "city": "Paris", "lat": 48.8554, "lng": 2.3450, "category": "Culture", "cost": 13, "best_time": "Morning (10:00 - 11:30)", "desc": "Gothic royal chapel featuring 1,113 radiant 13th-century stained glass panels that flood the room in violet light."}
        ]
    },
    "rome": {
        "name": "Rome, Italy",
        "country": "Italy",
        "tagline": "The Eternal City: Glories of Antiquity & Dolce Vita",
        "description": "An open-air museum where ancient ruins stand seamlessly alongside buzzing espresso bars.",
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [41.9028, 12.4964],
        "climate": "Sunny Mediterranean. Warm, pleasant spring (April-June) and mild autumn (September-November).",
        "recommended_duration": 4,
        "currency": "EUR",
        "cost_tier": "Moderate",
        "popular_interests": ["Ancient History", "Culinary & Wine", "Architecture", "Religious Heritage"],
        "customs": [
            "Cappuccino is traditionally an exclusively morning drink; order espresso after lunch or dinner.",
            "Cover shoulders and knees when visiting Saint Peter's and all Roman churches.",
            "Toss a coin over your left shoulder into the Trevi Fountain to guarantee your return to Rome."
        ],
        "emergency": {"police": "113", "ambulance": "118", "general_emergency": "112"},
        "spots": [
            {"name": "Colosseum & Roman Forum", "city": "Rome", "lat": 41.8902, "lng": 12.4922, "category": "Culture", "cost": 24, "best_time": "Morning (08:30 - 12:00)", "desc": "Step into gladiatorial arena history and stroll through the civic and religious epicenter of ancient Rome."},
            {"name": "Vatican Museums & Sistine Chapel", "city": "Rome", "lat": 41.9065, "lng": 12.4536, "category": "Culture", "cost": 28, "best_time": "Morning (08:30 - 12:30)", "desc": "Marvel at Michelangelo's ceiling frescoes and the overwhelming grandeur of St. Peter's Basilica."},
            {"name": "Pantheon & Piazza della Rotonda", "city": "Rome", "lat": 41.8986, "lng": 12.4769, "category": "Sightseeing", "cost": 5, "best_time": "Afternoon (14:00 - 15:30)", "desc": "The best-preserved ancient monument in Rome featuring the world's largest unreinforced concrete dome."},
            {"name": "Trevi Fountain Coin Toss & Artisanal Gelato", "city": "Rome", "lat": 41.9009, "lng": 12.4833, "category": "Sightseeing", "cost": 6, "best_time": "Evening (19:30 - 21:00)", "desc": "Baroque masterwork fountain carved from Travertine stone, followed by pistachio gelato."},
            {"name": "Trastevere Cobblestone Culinary Wander", "city": "Rome", "lat": 41.8894, "lng": 12.4707, "category": "Dining", "cost": 38, "best_time": "Evening (19:30 - 22:30)", "desc": "Charming ivy-draped neighborhood famous for authentic Cacio e Pepe, Carbonara, and lively wine osterias."}
        ]
    },
    "bali": {
        "name": "Bali, Indonesia",
        "country": "Indonesia",
        "tagline": "Island of the Gods: Emerald Terraces, Coastal Temples & Wellness",
        "description": "Tropical paradise of lush volcanoes, sacred Hindu water temples, world-class surf breaks, and wellness sanctuaries.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [-8.4095, 115.1889],
        "climate": "Tropical warm climate year-round. Dry sunny season runs from April to October.",
        "recommended_duration": 6,
        "currency": "USD",
        "cost_tier": "Value / Moderate",
        "popular_interests": ["Beaches & Surfing", "Spiritual & Temples", "Wellness & Yoga", "Scenic Waterfalls"],
        "customs": [
            "Wear a sash and sarong when entering any Balinese temple complex.",
            "Do not step on daily canang sari flower offerings placed respectfully on footpaths.",
            "Use your right hand when giving or receiving items; touching heads is impolite."
        ],
        "emergency": {"police": "110", "ambulance": "118", "tourist_police": "+62-361-754590"},
        "spots": [
            {"name": "Uluwatu Clifftop Temple & Sunset Kecak Fire Dance", "city": "Bali", "lat": -8.8291, "lng": 115.0849, "category": "Culture", "cost": 15, "best_time": "Evening (17:00 - 19:30)", "desc": "Perched 70 meters atop steep ocean cliffs with hypnotic chanting and dramatic Indian Ocean sunset vistas."},
            {"name": "Tegallalang Rice Terraces & Jungle Swing", "city": "Bali", "lat": -8.4312, "lng": 115.2818, "category": "Nature", "cost": 10, "best_time": "Morning (08:00 - 10:30)", "desc": "Verdant stepped emerald hills showcasing traditional Balinese subak communal irrigation systems."},
            {"name": "Ubud Sacred Monkey Forest Sanctuary", "city": "Bali", "lat": -8.5190, "lng": 115.2606, "category": "Nature", "cost": 6, "best_time": "Morning (09:00 - 11:00)", "desc": "Enchanted moss-draped ancient banyan jungle inhabited by over 1,000 playful long-tailed macaques."},
            {"name": "Tanah Lot Ocean Rock Temple", "city": "Bali", "lat": -8.6212, "lng": 115.0868, "category": "Culture", "cost": 5, "best_time": "Evening (16:30 - 18:30)", "desc": "Iconic offshore sea temple perched on an offshore wave-swept black volcanic rock formation."},
            {"name": "Tegenungan Waterfall & River Gorge", "city": "Bali", "lat": -8.5753, "lng": 115.2898, "category": "Nature", "cost": 3, "best_time": "Afternoon (13:00 - 15:00)", "desc": "Powerful rushing cascade set within a dramatic tropical jungle gorge with natural swimming pools."}
        ]
    },
    "jaipur": {
        "name": "Jaipur, India",
        "country": "India",
        "tagline": "The Pink City: Royal Palaces, Majestic Hill Forts & Vibrant Bazaars",
        "description": "Rajasthan's historic capital renowned for its terracotta-pink architecture, UNESCO hill forts, royal palaces, and rich textile traditions.",
        "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [26.9124, 75.7873],
        "climate": "Semi-arid climate. Pleasant sunny winters (Oct–March) ideal for sightseeing; warm summers.",
        "recommended_duration": 4,
        "currency": "INR",
        "cost_tier": "Moderate",
        "popular_interests": ["Culture & History", "Heritage Forts", "Culinary & Dining", "Local Markets", "Scenic Photography"],
        "customs": [
            "Dress modestly when visiting historic forts and sacred temples; remove shoes at temple entrances.",
            "Bargaining with a warm smile is customary and polite in traditional bazaars like Johari and Bapu Bazaar.",
            "Enjoy traditional Rajasthani Dal Baati Churma, Pyaaz Kachori, and Ghewar sweets from authentic local eateries.",
            "Keep small cash denominations handy for auto-rickshaws and street vendors."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "102 / 108", "tourist_helpline": "1363"},
        "spots": [
            {"name": "Amber Fort & Palace (Amer)", "city": "Jaipur", "lat": 26.9855, "lng": 75.8513, "category": "Culture", "cost": 100, "best_time": "Morning (08:30 - 11:30)", "desc": "Majestic UNESCO hilltop fortress featuring the breathtaking Sheesh Mahal (Mirror Palace) and Maota Lake vistas."},
            {"name": "Hawa Mahal (Palace of Winds)", "city": "Jaipur", "lat": 26.9239, "lng": 75.8267, "category": "Sightseeing", "cost": 50, "best_time": "Morning (09:00 - 10:30)", "desc": "Iconic five-story pink sandstone facade with 953 jharokhas windows designed for royal women."},
            {"name": "City Palace & Chandra Mahal", "city": "Jaipur", "lat": 26.9258, "lng": 75.8237, "category": "Culture", "cost": 300, "best_time": "Afternoon (13:30 - 16:00)", "desc": "Grand royal residence blending Rajput and Mughal architecture, housing museum courtyards and the Maharaja's armory."},
            {"name": "Jantar Mantar Royal Observatory", "city": "Jaipur", "lat": 26.9248, "lng": 75.8246, "category": "Culture", "cost": 50, "best_time": "Afternoon (11:30 - 13:00)", "desc": "UNESCO World Heritage astronomical monument with the world's largest stone sundial."},
            {"name": "Nahargarh Fort Sunset Viewpoint", "city": "Jaipur", "lat": 26.9373, "lng": 75.8155, "category": "Sightseeing", "cost": 50, "best_time": "Evening (17:00 - 19:30)", "desc": "Perched on the rugged Aravalli ridge, offering golden-hour sunset panoramas overlooking all of Jaipur."},
            {"name": "Johari Bazaar & Bapu Bazaar Walk", "city": "Jaipur", "lat": 26.9210, "lng": 75.8250, "category": "Shopping", "cost": 0, "best_time": "Afternoon (15:00 - 18:00)", "desc": "Vibrant pink-walled market streets famous for authentic block-print quilts, blue pottery, and silver jewelry."},
            {"name": "Albert Hall Museum", "city": "Jaipur", "lat": 26.9116, "lng": 75.8195, "category": "Culture", "cost": 40, "best_time": "Morning (10:00 - 12:00)", "desc": "Stunning Indo-Saracenic palace museum displaying royal weaponry, Persian carpets, and miniature paintings."},
            {"name": "Jal Mahal (Water Palace)", "city": "Jaipur", "lat": 26.9535, "lng": 75.8462, "category": "Sightseeing", "cost": 0, "best_time": "Evening (18:00 - 19:00)", "desc": "Picturesque palace floating serenely in the middle of Man Sagar Lake, mesmerizing when illuminated at twilight."},
            {"name": "Chokhi Dhani Ethnic Cultural Village", "city": "Jaipur", "lat": 26.7663, "lng": 75.8362, "category": "Dining", "cost": 900, "best_time": "Evening (18:30 - 22:00)", "desc": "Immersive Rajasthani village carnival with traditional folk dances, puppet acts, and royal thali banquet."}
        ]
    },
    "dehradun": {
        "name": "Dehradun, India",
        "country": "India",
        "tagline": "Doon Valley: Colonial Charms, River Caves & Himalayan Foothills",
        "description": "Nestled in the Doon Valley between the Ganges and Yamuna rivers, Dehradun offers picturesque nature, ancient cave temples, and academic institutions.",
        "image_url": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [30.3165, 78.0322],
        "climate": "Pleasant sub-tropical climate. Cool crisp winters and temperate spring/summer weather.",
        "recommended_duration": 3,
        "currency": "INR",
        "cost_tier": "Value / Moderate",
        "popular_interests": ["Nature & Caves", "Heritage & Architecture", "Local Bazaars", "Himalayan Vistas"],
        "customs": [
            "Dehradun is a peaceful valley town; enjoy relaxed morning walks in colonial cantonment areas.",
            "Wear waterproof footwear when exploring the natural limestone stream at Robber's Cave.",
            "Sample famous Doon bakery treats (rusks, plum cakes) at Ellora's Melting Moments on Rajpur Road."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "108", "tourist_helpline": "1363"},
        "spots": [
            {"name": "Robber's Cave (Guchhupani Gorge)", "city": "Dehradun", "lat": 30.3773, "lng": 78.0610, "category": "Nature", "cost": 35, "best_time": "Morning (09:00 - 12:00)", "desc": "Natural 600-meter limestone river cave where travelers wade barefoot through cool flowing knee-deep springs."},
            {"name": "Mindrolling Buddhist Monastery & Great Stupa", "city": "Dehradun", "lat": 30.2608, "lng": 78.0125, "category": "Culture", "cost": 0, "best_time": "Afternoon (13:30 - 16:00)", "desc": "One of the largest Buddhist centers in India, featuring a 185-foot Great Stupa, tranquil prayer gardens, and gold murals."},
            {"name": "Forest Research Institute (FRI) Heritage Campus", "city": "Dehradun", "lat": 30.3426, "lng": 77.9996, "category": "Culture", "cost": 40, "best_time": "Morning (09:30 - 12:30)", "desc": "Colonial Greco-Roman brick marvel larger than Buckingham Palace, surrounded by lush botanical arboretums."},
            {"name": "Sahastradhara Sulphur Springs & Waterfalls", "city": "Dehradun", "lat": 30.3842, "lng": 78.1287, "category": "Nature", "cost": 20, "best_time": "Afternoon (14:00 - 16:30)", "desc": "'Thousandfold springs' dripping over moss-covered limestone stalactites, known for therapeutic waters."},
            {"name": "Paltan Bazaar & Famous Clock Tower (Ghanta Ghar)", "city": "Dehradun", "lat": 30.3244, "lng": 78.0418, "category": "Shopping", "cost": 0, "best_time": "Evening (17:30 - 20:30)", "desc": "Bustling central bazaar renowned for authentic basmati rice, woolens, wooden handicrafts, and street chaat."}
        ]
    },
    "rishikesh": {
        "name": "Rishikesh, India",
        "country": "India",
        "tagline": "Yoga Capital of the World & Spiritual Gateway to the Garhwal Himalayas",
        "description": "Perched where the turquoise holy Ganges emerges from the Himalayas, Rishikesh blends yoga ashrams, river rafting, and devotional aartis.",
        "image_url": "https://images.unsplash.com/photo-1600100397608-f010e42f9b84?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [30.0869, 78.2676],
        "climate": "Crisp mountain air. Optimal visiting months are September through April.",
        "recommended_duration": 3,
        "currency": "INR",
        "cost_tier": "Value / Moderate",
        "popular_interests": ["Spiritual & Yoga", "River Rafting", "Scenic Ganges Ghats", "Mountain Cafes"],
        "customs": [
            "Rishikesh is an entirely vegetarian and alcohol-free sacred holy town.",
            "Dress respectfully covering shoulders and knees; maintain quiet reverence along the river ghats."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "108"},
        "spots": [
            {"name": "Triveni Ghat Evening Maha Aarti", "city": "Rishikesh", "lat": 30.1048, "lng": 78.2917, "category": "Culture", "cost": 0, "best_time": "Evening (18:00 - 19:30)", "desc": "Soul-stirring twilight Ganga Aarti ceremony where hundreds of brass oil lamps illuminate the sacred river confluence."},
            {"name": "Ram Jhula, Laxman Jhula & Swargashram", "city": "Rishikesh", "lat": 30.1235, "lng": 78.3150, "category": "Sightseeing", "cost": 0, "best_time": "Morning (08:30 - 11:30)", "desc": "Iconic iron suspension bridges spanning the turquoise Ganges, linking historic bookshops, ashrams, and organic cafes."},
            {"name": "The Beatles Ashram (Chaurasi Kutia)", "city": "Rishikesh", "lat": 30.1165, "lng": 78.3130, "category": "Culture", "cost": 150, "best_time": "Morning (09:30 - 12:30)", "desc": "Historic 1968 meditation retreat of The Beatles, featuring 84 meditation caves and vibrant pop-art graffiti murals."},
            {"name": "White Water Ganges River Rafting (Shivpuri)", "city": "Rishikesh", "lat": 30.1380, "lng": 78.3890, "category": "Nature", "cost": 800, "best_time": "Morning (09:00 - 13:00)", "desc": "Thrilling 16 km whitewater rapids through the Garhwal mountain gorge with body surfing and cliff jumping."},
            {"name": "Neer Garh Waterfall Trek", "city": "Rishikesh", "lat": 30.1448, "lng": 78.3340, "category": "Nature", "cost": 30, "best_time": "Afternoon (14:00 - 16:30)", "desc": "Refreshing jungle trek leading to multi-tiered turquoise natural cascade pools nestled in the hills."}
        ]
    },
    "mussoorie": {
        "name": "Mussoorie, India",
        "country": "India",
        "tagline": "Queen of the Hills: Colonial Promenades, Cascades & Himalayan Panoramas",
        "description": "Established by the British in the 1820s atop a Garhwal mountain ridge, Mussoorie offers misty valley panoramas and refreshing mountain retreats.",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [30.4598, 78.0644],
        "climate": "Cool mountain temperate climate. Foggy monsoons, snow flurries in deep winter (Jan).",
        "recommended_duration": 3,
        "currency": "INR",
        "cost_tier": "Moderate",
        "popular_interests": ["Hill Station Vistas", "Waterfalls", "Colonial Heritage", "Mall Road Promenade"],
        "customs": [
            "Carry a warm layer or windcheater as evening mountain breezes turn chilly quickly.",
            "The Mall Road is pedestrianized in the evenings; enjoy peaceful strolls without vehicular traffic."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "108"},
        "spots": [
            {"name": "Kempty Falls Mountain Cascades", "city": "Mussoorie", "lat": 30.4855, "lng": 78.0310, "category": "Nature", "cost": 50, "best_time": "Morning (09:00 - 12:00)", "desc": "Spectacular 40-foot waterfall tumbling down mountain cliffs into a refreshing splash basin."},
            {"name": "Mall Road & Camel's Back Road Walk", "city": "Mussoorie", "lat": 30.4580, "lng": 78.0740, "category": "Sightseeing", "cost": 0, "best_time": "Evening (17:30 - 20:00)", "desc": "Scenic 3 km peaceful ridge promenade overlooking the sunset valley, shaped like a camel's hump."},
            {"name": "Gun Hill Viewpoint & Cable Car", "city": "Mussoorie", "lat": 30.4605, "lng": 78.0775, "category": "Sightseeing", "cost": 150, "best_time": "Afternoon (15:00 - 17:30)", "desc": "Second highest peak in Mussoorie accessed by a 400-meter ropeway with 360-degree snow-capped Himalayan vistas."},
            {"name": "George Everest House & Cloud's End Hike", "city": "Mussoorie", "lat": 30.4612, "lng": 78.0125, "category": "Nature", "cost": 20, "best_time": "Morning (09:30 - 12:30)", "desc": "Historic 1832 estate of Sir George Everest perched dramatically atop a cliff with panoramic Doon Valley views."},
            {"name": "Lal Tibba Scenic Sunset Viewpoint", "city": "Mussoorie", "lat": 30.4650, "lng": 78.0980, "category": "Nature", "cost": 50, "best_time": "Evening (17:00 - 18:30)", "desc": "Highest point in Mussoorie (Landour) with high-powered telescopes framing Kedarnath, Badrinath, and snow peaks."}
        ]
    },
    "haridwar": {
        "name": "Haridwar, India",
        "country": "India",
        "tagline": "Gateway of the Gods: Sacred Ganges Ghats & Timeless Pilgrimage Rituals",
        "description": "One of India's seven holiest Hindu cities, where the sacred Ganges enters the Indo-Gangetic Plains amidst ancient ghats and temple bells.",
        "image_url": "https://images.unsplash.com/photo-1596401057633-54a8fe8ef647?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [29.9457, 78.1642],
        "climate": "Warm sub-tropical. Pleasant winters (Oct-March); holy bathing in the crisp mountain-fed river.",
        "recommended_duration": 2,
        "currency": "INR",
        "cost_tier": "Value / Moderate",
        "popular_interests": ["Sacred Ghats & Ganga Aarti", "Ancient Temples", "Heritage Bazaars", "Spiritual Rituals"],
        "customs": [
            "Haridwar is a sacred vegetarian holy city; alcohol and non-veg food are strictly prohibited.",
            "Remove footwear before walking onto the stone steps of Har Ki Pauri and bathing ghats."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "108"},
        "spots": [
            {"name": "Har Ki Pauri & Evening Ganga Aarti", "city": "Haridwar", "lat": 29.9567, "lng": 78.1706, "category": "Culture", "cost": 0, "best_time": "Evening (17:30 - 19:30)", "desc": "The most revered bathing ghat on the Ganges, featuring a breathtaking evening Aarti with thousands of floating leaf lamps."},
            {"name": "Mansa Devi Temple & Udankhatola Cable Car", "city": "Haridwar", "lat": 29.9610, "lng": 78.1620, "category": "Culture", "cost": 120, "best_time": "Morning (08:30 - 11:30)", "desc": "Hilltop shrine atop Bilwa Parvat dedicated to wish-fulfilling goddess Mansa Devi, offering views over Haridwar."},
            {"name": "Moti Bazaar Heritage Food & Souvenir Walk", "city": "Haridwar", "lat": 29.9520, "lng": 78.1670, "category": "Shopping", "cost": 0, "best_time": "Afternoon (14:00 - 17:00)", "desc": "Centuries-old market lanes famous for brass idols, rudraksha malas, and famous Mohan Ji Poori Wale hot meals."},
            {"name": "Chandi Devi Temple Hilltop Pilgrimage", "city": "Haridwar", "lat": 29.9280, "lng": 78.1810, "category": "Culture", "cost": 140, "best_time": "Morning (09:00 - 12:00)", "desc": "Commanding temple perched atop Neel Parvat on the opposite bank of the Ganges, accessed by ropeway."}
        ]
    },
    "delhi": {
        "name": "New Delhi, India",
        "country": "India",
        "tagline": "Historic Capital of Empires, Heritage Monoliths & Street Food Delights",
        "description": "India's vibrant capital, where Mughal fortresses and ancient minarets coexist with grand colonial avenues.",
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [28.6139, 77.2090],
        "climate": "Crisp pleasant winters (Nov-Feb), warm summers, monsoon July-Aug.",
        "recommended_duration": 4,
        "currency": "INR",
        "cost_tier": "Moderate",
        "popular_interests": ["History & Heritage", "Culinary & Street Food", "Architecture", "Shopping"],
        "customs": [
            "Use the clean, air-conditioned Delhi Metro for fast transit across the National Capital Region.",
            "Cover heads and remove shoes when visiting Jama Masjid, Gurudwara Bangla Sahib, and temples."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "102 / 108"},
        "spots": [
            {"name": "Red Fort (Lal Qila)", "city": "Delhi", "lat": 28.6562, "lng": 77.2410, "category": "Culture", "cost": 50, "best_time": "Morning (09:00 - 11:30)", "desc": "Grand 17th-century Mughal red sandstone imperial palace complex."},
            {"name": "Qutub Minar & Mehrauli Heritage Park", "city": "Delhi", "lat": 28.5244, "lng": 77.1855, "category": "Culture", "cost": 50, "best_time": "Morning (09:30 - 12:00)", "desc": "Soaring 73-meter victory minaret and ancient iron pillar that has never rusted."},
            {"name": "Humayun's Tomb Garden Complex", "city": "Delhi", "lat": 28.5933, "lng": 77.2507, "category": "Culture", "cost": 50, "best_time": "Afternoon (14:00 - 16:30)", "desc": "Majestic UNESCO garden tomb that served as the architectural prototype for the Taj Mahal."},
            {"name": "Chandni Chowk & Paranthe Wali Gali", "city": "Delhi", "lat": 28.6505, "lng": 77.2303, "category": "Dining", "cost": 300, "best_time": "Afternoon (12:30 - 15:30)", "desc": "Historic Old Delhi market alleys famous for stuffed fried flatbreads, jalebis, and chaat."}
        ]
    },
    "goa": {
        "name": "Goa, India",
        "country": "India",
        "tagline": "Sun-Kissed Beaches, Portuguese Heritage & Laid-back Coastal Charm",
        "description": "India's beloved coastal haven known for golden shores, colonial churches, water sports, and beach shacks.",
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [15.2993, 74.1240],
        "climate": "Tropical maritime climate with balmy sea breezes throughout winter.",
        "recommended_duration": 5,
        "currency": "INR",
        "cost_tier": "Moderate",
        "popular_interests": ["Beaches & Coastal", "Water Sports", "Nightlife", "Seafood & Dining"],
        "customs": [
            "Rent scooters or open jeeps to leisurely explore both North and South Goa beaches.",
            "Try authentic Goan fish curry thali with fresh catch of the day at beach shacks."
        ],
        "emergency": {"police": "100 / 112", "ambulance": "108"},
        "spots": [
            {"name": "Fort Aguada & Lighthouse Viewpoint", "city": "Goa", "lat": 15.4920, "lng": 73.7735, "category": "Sightseeing", "cost": 50, "best_time": "Morning (09:00 - 11:30)", "desc": "17th-century Portuguese fortress overlooking the vast Arabian Sea coastline."},
            {"name": "Basilica of Bom Jesus (Old Goa)", "city": "Goa", "lat": 15.5009, "lng": 73.9116, "category": "Culture", "cost": 0, "best_time": "Afternoon (13:30 - 15:30)", "desc": "UNESCO baroque church holding the sacred relics of St. Francis Xavier."},
            {"name": "Anjuna & Vagator Sunset Beach Promenade", "city": "Goa", "lat": 15.5807, "lng": 73.7438, "category": "Nature", "cost": 0, "best_time": "Evening (17:00 - 19:30)", "desc": "Dramatic red laterite cliffs, swaying palm groves, and vibrant seaside sunset cafes."}
        ]
    }
}

# =========================================================================
# STATE & REGIONAL CIRCUIT REGISTRY
# =========================================================================
STATE_REGION_REGISTRY = {
    "uttarakhand": {
        "name": "Uttarakhand",
        "aliases": ["uttrakhand", "uttaranchal", "uttranchal"],
        "country": "India",
        "coordinates": [30.0668, 78.3000],
        "tagline": "Devbhoomi: Holy Ganges, Himalayan Vistas, Yoga Sanctuaries & Colonial Hills",
        "description": "The sacred Land of the Gods, uniting spiritual river ghats in Haridwar & Rishikesh with scenic valley capitals in Dehradun and mist-clad British hill stations in Mussoorie.",
        "climate": "Invigorating mountain weather. Pleasant cool summers, refreshing monsoon greenery, crisp sunny winters.",
        "currency": "INR",
        "cost_tier": "Value / Moderate",
        "emergency": {"police": "100 / 112", "ambulance": "108", "tourist_helpline": "1363"},
        "hubs": ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
        "circuits": {
            2: ["Haridwar", "Rishikesh"],
            3: ["Haridwar", "Rishikesh"],
            4: ["Haridwar", "Rishikesh", "Dehradun"],
            5: ["Haridwar", "Rishikesh", "Dehradun"],
            6: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
            7: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
            8: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
            9: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
            10: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
            12: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"],
            14: ["Haridwar", "Rishikesh", "Dehradun", "Mussoorie"]
        },
        "transit_style": "Mountain highway cabs, shared Sumos, and UTC express buses (approx. 45–90 mins between circuit hubs)."
    },
    "uttrakhand": {
        "alias_of": "uttarakhand"
    },
    "uttaranchal": {
        "alias_of": "uttarakhand"
    },
    "uttranchal": {
        "alias_of": "uttarakhand"
    },
    "himachal": {
        "name": "Himachal Pradesh",
        "country": "India",
        "coordinates": [31.1048, 77.1734],
        "tagline": "Land of the Gods: Alpine Valleys, Colonial Ridges & Apple Orchards",
        "description": "Dramatic Himalayan valleys spanning colonial heritage in Shimla, adventure and river gorges in Kullu-Manali, and spiritual Tibetan sanctuaries in Dharamshala.",
        "climate": "Alpine mountain climate. Crisp summers and snowy winters.",
        "currency": "INR",
        "cost_tier": "Moderate",
        "emergency": {"police": "100 / 112", "ambulance": "108"},
        "hubs": ["Shimla", "Kullu", "Manali", "Kasol", "Dharamshala"],
        "circuits": {
            3: ["Shimla"],
            4: ["Shimla", "Manali"],
            5: ["Shimla", "Kullu", "Manali"],
            6: ["Shimla", "Manali", "Kasol"],
            7: ["Shimla", "Manali", "Kasol", "Dharamshala"]
        },
        "transit_style": "Scenic hill highway buses (HRTC) and private tourist taxis across mountain passes."
    },
    "himachal pradesh": {
        "alias_of": "himachal"
    },
    "rajasthan": {
        "name": "Rajasthan",
        "country": "India",
        "coordinates": [26.9124, 75.7873],
        "tagline": "Land of Kings: Desert Citadels, Royal Havelis & Golden Sands",
        "description": "The majestic desert empire of Rajput kings, weaving the Pink City of Jaipur with the Blue City of Jodhpur and the romantic City of Lakes in Udaipur.",
        "climate": "Semi-arid sunny weather. Optimal sightseeing from October through March.",
        "currency": "INR",
        "cost_tier": "Moderate",
        "emergency": {"police": "100 / 112", "ambulance": "108", "tourist_helpline": "1363"},
        "hubs": ["Jaipur", "Jodhpur", "Udaipur", "Jaisalmer"],
        "circuits": {
            3: ["Jaipur"],
            4: ["Jaipur", "Jodhpur"],
            5: ["Jaipur", "Jodhpur"],
            6: ["Jaipur", "Jodhpur", "Udaipur"],
            7: ["Jaipur", "Jodhpur", "Udaipur"]
        },
        "transit_style": "Intercity express trains (Vande Bharat / Shatabdi) and AC sleeper highway buses."
    },
    "kerala": {
        "name": "Kerala",
        "country": "India",
        "coordinates": [9.9312, 76.2673],
        "tagline": "God's Own Country: Emerald Backwaters, Spice Hills & Tea Plantations",
        "description": "A tropical coastal haven leading from port heritage in Fort Kochi into misty tea hills in Munnar and serene backwater houseboats in Alleppey.",
        "climate": "Warm tropical maritime climate with balmy sea breezes.",
        "currency": "INR",
        "cost_tier": "Moderate",
        "emergency": {"police": "100 / 112", "ambulance": "108"},
        "hubs": ["Kochi", "Munnar", "Thekkady", "Alleppey"],
        "circuits": {
            3: ["Kochi", "Munnar"],
            4: ["Kochi", "Munnar", "Alleppey"],
            5: ["Kochi", "Munnar", "Alleppey"],
            6: ["Kochi", "Munnar", "Thekkady", "Alleppey"],
            7: ["Kochi", "Munnar", "Thekkady", "Alleppey"]
        },
        "transit_style": "AC chauffeur cars, scenic hill road tourist cabs, and serene backwater ferries."
    }
}

COUNTRY_STOPWORDS = {
    "india", "usa", "uk", "france", "japan", "italy", "indonesia", "germany",
    "spain", "canada", "australia", "united states", "united kingdom"
}

def parse_multi_city(dest_str: str) -> Optional[List[str]]:
    """Detects if user explicitly entered a multi-city route (e.g. 'Dehradun, Mussoorie, and Rishikesh')."""
    raw = dest_str.replace(" and ", ",").replace(" & ", ",").replace(" - ", ",").replace(" to ", ",")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    cities = [p for p in parts if p.lower() not in COUNTRY_STOPWORDS]
    if len(cities) >= 2:
        return [c.title() for c in cities]
    return None

def classify_destination(destination_query: str, duration_days: int = 5) -> Dict[str, Any]:
    """
    Classifies destination input into:
    - SINGLE_CITY: Focused single city destination (e.g. Jaipur, Dehradun, Paris)
    - MULTI_CITY: Explicit user multi-destination input (e.g. "Dehradun, Mussoorie, and Rishikesh")
    - STATE_REGION: State or large region territory requiring circuit selection (e.g. Uttarakhand, Rajasthan)
    """
    dest_clean = destination_query.strip()
    dest_lower = dest_clean.lower()
    clean_core = re.sub(r"(?i)\s*,\s*india$", "", dest_clean).strip()
    clean_core_lower = clean_core.lower()

    # 1. User-specified explicit multi-city route (e.g. "Dehradun, Mussoorie, and Rishikesh")
    multi_cities = parse_multi_city(dest_clean)
    if multi_cities and len(multi_cities) >= 2:
        return {
            "type": "MULTI_CITY",
            "primary_name": " - ".join(multi_cities),
            "cities": [c.title() for c in multi_cities],
            "is_multi": True,
            "region_key": None
        }

    # 2. Single City Check (e.g., "Dehradun", "Jaipur", "Paris", "Tokyo")
    first_token = dest_clean.split(",")[0].strip().lower()
    if first_token in DESTINATIONS_DATA:
        city_name = dest_clean.split(",")[0].strip().title()
        return {
            "type": "SINGLE_CITY",
            "primary_name": city_name,
            "cities": [city_name],
            "is_multi": False,
            "region_key": None
        }

    # 3. State or large territory check
    for key, reg_data in STATE_REGION_REGISTRY.items():
        if "alias_of" in reg_data:
            real_key = reg_data["alias_of"]
            data = STATE_REGION_REGISTRY[real_key]
        else:
            real_key = key
            data = reg_data

        name_lower = data.get("name", "").lower()
        aliases = [key, name_lower] + [a.lower() for a in data.get("aliases", [])]

        matched = False
        for a in aliases:
            if a == clean_core_lower or a in dest_lower or clean_core_lower in a:
                matched = True
                break

        if matched:
            circuit_map = data.get("circuits", {})
            durations = sorted(circuit_map.keys())
            eff_dur = min(durations, key=lambda d: abs(d - duration_days)) if durations else duration_days
            selected_cities = circuit_map.get(eff_dur, data.get("hubs", [])[:4])
            return {
                "type": "STATE_REGION",
                "primary_name": f"{data['name']} Circuit ({', '.join(selected_cities)})",
                "region_key": real_key,
                "region_name": data["name"],
                "cities": selected_cities,
                "is_multi": True
            }

    # 4. Fallback: Single City
    city_name = dest_clean.split(",")[0].strip().title()
    return {
        "type": "SINGLE_CITY",
        "primary_name": city_name,
        "cities": [city_name],
        "is_multi": False,
        "region_key": None
    }

def get_destination_data(destination_query: str, duration_days: int = 5) -> Dict[str, Any]:
    """
    Finds matching destination or generates realistic synthesis for custom cities and state routes.
    """
    classification = classify_destination(destination_query, duration_days=duration_days)
    q = destination_query.lower().strip()
    
    # 1. Multi-City or State Region Route
    if classification["is_multi"]:
        circuit_cities = classification["cities"]
        region_key = classification.get("region_key")
        reg_info = STATE_REGION_REGISTRY.get(region_key, {}) if region_key else {}
        if "alias_of" in reg_info:
            reg_info = STATE_REGION_REGISTRY.get(reg_info["alias_of"], {})

        # Collect spots from each circuit city
        aggregated_spots = []
        for city in circuit_cities:
            c_key = city.lower().strip()
            city_data = DESTINATIONS_DATA.get(c_key)
            if city_data and "spots" in city_data:
                for s in city_data["spots"]:
                    s_copy = dict(s)
                    s_copy["city"] = city
                    aggregated_spots.append(s_copy)
            else:
                # Synthesize realistic city-anchored spot
                aggregated_spots.extend([
                    {
                        "name": f"{city} Historic Center & Highlights",
                        "city": city,
                        "lat": 30.0, "lng": 78.0,
                        "category": "Culture", "cost": 50,
                        "best_time": "Morning (09:00 - 12:00)",
                        "desc": f"Experience the central landmark, cultural heritage, and morning atmosphere in {city}."
                    },
                    {
                        "name": f"{city} Scenic Viewpoint & Promenade",
                        "city": city,
                        "lat": 30.01, "lng": 78.01,
                        "category": "Sightseeing", "cost": 20,
                        "best_time": "Afternoon (14:00 - 17:00)",
                        "desc": f"Panoramic mountain vistas and local market exploration in {city}."
                    }
                ])

        first_city_key = circuit_cities[0].lower().strip()
        first_city_data = DESTINATIONS_DATA.get(first_city_key, {})
        base_coords = first_city_data.get("coordinates") or reg_info.get("coordinates") or [30.0668, 78.3000]

        return {
            "name": classification["primary_name"],
            "destination_type": classification["type"],
            "circuit_cities": circuit_cities,
            "is_multi_destination": True,
            "country": reg_info.get("country", "India"),
            "tagline": reg_info.get("tagline", f"Multi-Destination Journey Across {', '.join(circuit_cities)}"),
            "description": reg_info.get("description", f"A scenic circuit connecting {', '.join(circuit_cities)} with rich regional experiences."),
            "image_url": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80",
            "coordinates": base_coords,
            "climate": reg_info.get("climate", "Favorable seasonal sightseeing climate throughout the circuit."),
            "currency": reg_info.get("currency", "INR"),
            "cost_tier": reg_info.get("cost_tier", "Moderate"),
            "customs": [
                "Respect religious traditions and dress modestly at sacred ghats and temples.",
                "Allow realistic travel windows for mountain/highway transit between cities.",
                "Keep cash handy for local intercity taxis and market stalls."
            ],
            "emergency": reg_info.get("emergency", {"police": "100 / 112", "ambulance": "108", "tourist_helpline": "1363"}),
            "spots": aggregated_spots,
            "prime_areas": circuit_cities,
            "transit_style": reg_info.get("transit_style", "Intercity cabs, state express buses, and local auto-rickshaws between hubs.")
        }

    # 2. Check exact or partial key match in DESTINATIONS_DATA
    for key, data in DESTINATIONS_DATA.items():
        if key == q or data["name"].lower() == q or key in q:
            data_copy = dict(data)
            data_copy["destination_type"] = "SINGLE_CITY"
            data_copy["circuit_cities"] = [data["name"].split(",")[0].strip()]
            data_copy["is_multi_destination"] = False
            return data_copy

    capitalized = destination_query.title()
    is_india = any(c in q for c in [
        "india", "indore", "jaipur", "delhi", "mumbai", "bangalore", "bengaluru",
        "kolkata", "chennai", "hyderabad", "pune", "ahmedabad", "goa", "kerala",
        "varanasi", "agra", "udaipur", "jodhpur", "amritsar", "rishikesh", "manali",
        "shimla", "kochi", "surat", "lucknow", "bhopal", "patna", "vadodara", "nagpur",
        "dehradun", "mussoorie", "haridwar", "nainital", "uttarakhand", "himachal"
    ])

    if is_india:
        return {
            "name": capitalized,
            "destination_type": "SINGLE_CITY",
            "circuit_cities": [capitalized.split(",")[0].strip()],
            "is_multi_destination": False,
            "country": "India",
            "tagline": f"Discover the Heritage, Flavors & Vibrancy of {capitalized}",
            "description": f"A fascinating Indian destination offering rich regional culture, authentic local culinary delights, and unforgettable sightseeing.",
            "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
            "coordinates": [22.7196, 75.8577],
            "climate": "Pleasant seasonal sightseeing climate with comfortable temperatures.",
            "recommended_duration": 4,
            "currency": "INR",
            "cost_tier": "Moderate",
            "popular_interests": ["Culture & History", "Local Cuisine", "Bazaars & Markets", "Sightseeing"],
            "customs": [
                "Dress respectfully at religious and heritage spaces; remove footwear where indicated.",
                "Savor authentic regional dishes and fresh street snacks from trusted bustling eateries.",
                "Keep cash and UPI handy for auto-rickshaws, metro, and local market shopping."
            ],
            "emergency": {"police": "100 / 112", "ambulance": "102 / 108", "tourist_helpline": "1363"},
            "spots": [
                {"name": f"{capitalized} Historic Heritage Quarter", "city": capitalized, "lat": 22.72, "lng": 75.86, "category": "Culture", "cost": 50, "best_time": "Morning (09:00 - 11:30)", "desc": f"Explore architectural landmarks and centuries of local heritage in {capitalized}."},
                {"name": f"{capitalized} City Landmark & Museum", "city": capitalized, "lat": 22.73, "lng": 75.87, "category": "Culture", "cost": 100, "best_time": "Morning (11:30 - 13:30)", "desc": f"Discover historical relics, regional artwork, and cultural exhibits."},
                {"name": "Traditional Food Street & Sweet Market", "city": capitalized, "lat": 22.72, "lng": 75.85, "category": "Dining", "cost": 300, "best_time": "Afternoon (13:30 - 15:30)", "desc": f"Feast on authentic regional thalis, street savory snacks, and local sweets."},
                {"name": "Scenic Sunset Viewpoint & Lake Promenade", "city": capitalized, "lat": 22.74, "lng": 75.88, "category": "Nature", "cost": 0, "best_time": "Evening (17:30 - 19:30)", "desc": f"Unwind with scenic evening breezes and panoramic views over {capitalized}."}
            ]
        }

    # Generic intelligent fallback synthesizer for International destination
    return {
        "name": capitalized,
        "destination_type": "SINGLE_CITY",
        "circuit_cities": [capitalized.split(",")[0].strip()],
        "is_multi_destination": False,
        "country": "International",
        "tagline": f"Discover the Charms, Flavors & Landmarks of {capitalized}",
        "description": f"An extraordinary destination offering a rich blend of culture, local flavors, and memorable experiences tailored to your travel dreams.",
        "image_url": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80",
        "coordinates": [40.0, 20.0],
        "climate": "Pleasant seasonal conditions with optimal sightseeing weather throughout core seasons.",
        "recommended_duration": 5,
        "currency": "USD",
        "cost_tier": "Moderate",
        "popular_interests": ["Sightseeing", "Local Cuisine", "Cultural Highlights", "Walking Tours"],
        "customs": [
            "Greet locals warmly in their native language to show cultural appreciation.",
            "Carry a modest amount of cash for boutique markets and street stalls.",
            "Respect local etiquette at religious monuments and historical spaces."
        ],
        "emergency": {"police": "112", "ambulance": "112", "emergency": "911 / 112"},
        "spots": [
            {"name": f"{capitalized} Historic Old Town & Central Square", "city": capitalized, "lat": 40.01, "lng": 20.01, "category": "Culture", "cost": 0, "best_time": "Morning (09:00 - 11:30)", "desc": f"Explore the heart and soul of {capitalized}, admiring historic architecture and local street musicians."},
            {"name": f"{capitalized} National Art & Cultural Museum", "city": capitalized, "lat": 40.02, "lng": 20.02, "category": "Culture", "cost": 18, "best_time": "Morning (11:30 - 13:30)", "desc": f"Discover key artistic and historical treasures representing the heritage of the region."},
            {"name": "Authentic Local Market & Gastronomy Walk", "city": capitalized, "lat": 40.03, "lng": 20.01, "category": "Dining", "cost": 25, "best_time": "Afternoon (13:30 - 15:30)", "desc": f"Savor signature delicacies, farm-fresh produce, and baked goods from time-honored stalls."},
            {"name": "Scenic Panoramic Viewpoint & Botanical Gardens", "city": capitalized, "lat": 40.02, "lng": 20.03, "category": "Nature", "cost": 10, "best_time": "Afternoon (16:00 - 18:00)", "desc": f"Enjoy elevated views across the city skyline and picturesque landscapes as the afternoon cools."},
            {"name": "Traditional Evening Tavern / Dining Experience", "city": capitalized, "lat": 40.01, "lng": 20.02, "category": "Dining", "cost": 40, "best_time": "Evening (19:30 - 22:00)", "desc": f"Delight in regional specialties, hospitality, and convivial atmosphere in the lively district."}
        ]
    }
