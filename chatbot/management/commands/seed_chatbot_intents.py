from django.core.management.base import BaseCommand
from chatbot.models import ChatbotIntent

class Command(BaseCommand):
    help = 'Seeds initial chatbot intents and responses'
    
    def handle(self, *args, **options):
        # Define initial intents
        intents_data = [
            {
                'name': 'car_search',
                'description': 'Help with searching for cars',
                'pattern': 'how to search for cars, find cars, search cars, looking for car, find a car',
                'response': 'You can search for cars by using our search filters on the main page. You can filter by brand, model, year, price, and more!'
            },
            {
                'name': 'sell_car',
                'description': 'Information about selling a car',
                'pattern': 'how to sell my car, sell a car, selling car, list car, car listing',
                'response': 'To sell your car, you need to create an account and click on "Sell Your Car" button. You\'ll need to provide details and photos of your car.'
            },
            {
                'name': 'account_creation',
                'description': 'Help with account creation',
                'pattern': 'create account, sign up, register, join, new account',
                'response': 'To create an account, click on the "Register" link in the top menu and fill out the registration form with your details.'
            },
            {
                'name': 'login_help',
                'description': 'Help with logging in',
                'pattern': 'how to login, sign in, cannot login, login problem, forgot password',
                'response': 'To login, click on the "Login" link in the top menu. If you forgot your password, use the "Forgot Password" link on the login page.'
            },
            {
                'name': 'contact_seller',
                'description': 'Help with contacting sellers',
                'pattern': 'contact seller, message seller, talk to seller, ask seller',
                'response': 'You can contact a seller by clicking on the "Contact Seller" button on the car detail page. You\'ll need to be logged in to send messages.'
            },
            {
                'name': 'compare_cars',
                'description': 'Help with comparing cars',
                'pattern': 'compare cars, car comparison, how to compare',
                'response': 'You can add cars to your comparison list by clicking the "Compare" button on any car listing. Then view your comparison list by clicking on "Compare" in the top menu.'
            },
            {
                'name': 'pricing',
                'description': 'Information about car pricing',
                'pattern': 'car prices, pricing, how much, price range, average price',
                'response': 'Car prices on our platform vary based on brand, model, year, condition, and features. You can use our filters to find cars within your budget.'
            },
            {
                'name': 'favorites',
                'description': 'Help with favorites feature',
                'pattern': 'favorites, save car, bookmark, favorite cars',
                'response': 'You can save cars to your favorites by clicking the heart icon on any car listing. View your favorites by clicking on "Favorites" in the top menu.'
            },
            {
                'name': 'about_site',
                'description': 'Information about the website',
                'pattern': 'about dongelek, about website, what is dongelek, company info',
                'response': 'Dongelek is the largest car marketplace in Kazakhstan, connecting car buyers and sellers. We offer a secure platform with verified listings and user reviews.'
            },
            {
                'name': 'car_maintenance',
                'description': 'Information about car maintenance',
                'pattern': 'car maintenance, service car, maintain car, car service, oil change',
                'response': 'Regular car maintenance is important for keeping your vehicle in good condition. We recommend following the manufacturer\'s service schedule, usually in your car\'s manual. For used cars, it\'s good to check service history before purchase.'
            },
            {
                'name': 'fuel_efficiency',
                'description': 'Information about fuel efficiency',
                'pattern': 'fuel efficiency, gas mileage, fuel consumption, save fuel, economic car',
                'response': 'Fuel efficiency varies by car model and engine type. On Dongelek, you can filter cars by fuel type including efficient options like hybrids and electric vehicles. You can also check specific fuel consumption details on car listings.'
            },
            {
                'name': 'car_insurance',
                'description': 'Information about car insurance',
                'pattern': 'car insurance, insurance, insure car, vehicle insurance',
                'response': 'In Kazakhstan, car insurance is mandatory. The basic required insurance is OSAGO (Compulsory Motor Third Party Liability Insurance). When buying a car, you should arrange insurance before driving it. Some sellers might offer to transfer their existing policy.'
            },
            {
                'name': 'ev_cars',
                'description': 'Information about electric vehicles',
                'pattern': 'electric car, ev, electric vehicle, tesla, charging',
                'response': 'Dongelek lists electric vehicles from brands like Tesla, Nissan, and others. When buying an EV in Kazakhstan, consider the charging infrastructure in your area. You can filter for electric cars specifically on our search page.'
            },
            {
                'name': 'car_financing',
                'description': 'Information about car financing options',
                'pattern': 'car loan, finance car, auto loan, payment plan, car financing, buy car installments',
                'response': 'Many cars on Dongelek can be purchased with financing. You can arrange a car loan through most Kazakhstan banks, and some sellers offer in-house financing options. Check with your bank for current auto loan rates and eligibility.'
            },
            {
                'name': 'safety_ratings',
                'description': 'Information about car safety',
                'pattern': 'car safety, safety rating, safe car, safest cars, crash test',
                'response': 'Car safety is an important consideration. While Dongelek doesnt display formal safety ratings, you can research specific models on international safety rating websites like Euro NCAP. Newer cars typically have more advanced safety features.'
            },
            {
                'name': 'popular_brands',
                'description': 'Information about popular car brands',
                'pattern': 'popular brands, best brands, car brands, reliable brands',
                'response': 'Popular car brands in Kazakhstan include Toyota, Hyundai, Kia, Volkswagen, and Lexus. These brands are known for reliability and good service networks. You can browse all available brands using our search filters.'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for intent_data in intents_data:
            intent, created = ChatbotIntent.objects.update_or_create(
                name=intent_data['name'],
                defaults={
                    'description': intent_data['description'],
                    'pattern': intent_data['pattern'],
                    'response': intent_data['response']
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new intents and updated {updated_count} existing intents.'))
