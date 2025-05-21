# Entity-Relationship Diagram for Dongelek Car Marketplace

This document presents the ER diagram for the Dongelek car marketplace application, showing the relationships between different entities in the system.

## ER Diagram

```plantuml
@startuml Dongelek ER Diagram

!theme plain
skinparam linetype ortho
skinparam nodesep 70
skinparam ranksep 50
skinparam padding 10
skinparam backgroundColor white
skinparam classBackgroundColor #f5f5f5
skinparam classBorderColor #d5d5d5
skinparam arrowColor #707070

entity "User" as user {
  * id : int <<PK>>
  --
  username : varchar
  email : varchar
  password : varchar
  is_active : boolean
  is_seller : boolean
  is_buyer : boolean
  avatar : image
  about : text
  date_joined : datetime
}

entity "Brand" as brand {
  * id : int <<PK>>
  --
  name : varchar
}

entity "Model" as model {
  * id : int <<PK>>
  --
  name : varchar
  * brand_id : int <<FK>>
}

entity "Region" as region {
  * id : int <<PK>>
  --
  name : varchar
}

entity "City" as city {
  * id : int <<PK>>
  --
  name : varchar
  * region_id : int <<FK>>
}

entity "Car" as car {
  * id : int <<PK>>
  --
  * brand_id : int <<FK>>
  * model_id : int <<FK>>
  * seller_id : int <<FK>>
  * region_id : int <<FK>>
  * city_id : int <<FK>>
  year : int
  price : decimal
  mileage : int
  fuel_type : enum
  transmission : enum
  body_type : enum
  drive_type : enum
  color : varchar
  engine_size : float
  description : text
  slug : varchar
  is_active : boolean
  created_at : datetime
  views_count : int
}

entity "CarImage" as carimage {
  * id : int <<PK>>
  --
  * car_id : int <<FK>>
  image : image
  is_primary : boolean
  upload_date : datetime
}

entity "Favorite" as favorite {
  * id : int <<PK>>
  --
  * car_id : int <<FK>>
  * user_id : int <<FK>>
  created_at : datetime
}

entity "Compare" as compare {
  * id : int <<PK>>
  --
  * car_id : int <<FK>>
  * user_id : int <<FK>>
  added_at : datetime
}

entity "Conversation" as conversation {
  * id : int <<PK>>
  --
  * car_id : int <<FK>>
  * seller_id : int <<FK>>
  * buyer_id : int <<FK>>
  created_at : datetime
  last_message_at : datetime
}

entity "Message" as message {
  * id : int <<PK>>
  --
  * conversation_id : int <<FK>>
  * sender_id : int <<FK>>
  content : text
  is_read : boolean
  created_at : datetime
}

entity "SellerReview" as sellerreview {
  * id : int <<PK>>
  --
  * seller_id : int <<FK>>
  * reviewer_id : int <<FK>>
  * car_id : int <<FK>>
  rating : int
  comment : text
  is_verified : boolean
  is_edited : boolean
  created_at : datetime
  updated_at : datetime
}

entity "SellerRequest" as sellerrequest {
  * id : int <<PK>>
  --
  * user_id : int <<FK>>
  status : enum
  reason : text
  created_at : datetime
  updated_at : datetime
}

entity "ChatbotSession" as chatbotsession {
  * id : int <<PK>>
  --
  * user_id : int <<FK>>
  session_id : varchar
  created_at : datetime
}

entity "ChatbotMessage" as chatbotmessage {
  * id : int <<PK>>
  --
  * session_id : int <<FK>>
  user_message : text
  bot_response : text
  created_at : datetime
}

' Define relationships
brand ||--o{ model : "has"
region ||--o{ city : "has"
user ||--o{ car : "sells"
car }o--|| model : "is a"
car }o--|| brand : "is a"
car }o--|| region : "is located in"
car }o--|| city : "is located in"
car ||--o{ carimage : "has"
user ||--o{ favorite : "has"
car ||--o{ favorite : "is in"
user ||--o{ compare : "compares"
car ||--o{ compare : "is compared"
user ||--o{ conversation : "participates as seller"
user ||--o{ conversation : "participates as buyer"
car ||--o{ conversation : "is about"
conversation ||--o{ message : "contains"
user ||--o{ message : "sends"
user ||--o{ sellerreview : "receives as seller"
user ||--o{ sellerreview : "gives as reviewer"
car ||--o{ sellerreview : "is reviewed for"
user ||--o| sellerrequest : "requests"
user ||--o{ chatbotsession : "has"
chatbotsession ||--o{ chatbotmessage : "contains"

@enduml
```

## Entity Descriptions

### User
Represents users of the system, who can be buyers, sellers, or both.

### Brand and Model
Represents car brands and their associated models.

### Region and City
Geographic locations where cars are available.

### Car
The main entity representing a car listing with all its details.

### CarImage
Images associated with car listings, with one designated as primary.

### Favorite
Tracks which cars are favorited by which users.

### Compare
Tracks which cars are selected for comparison by which users.

### Conversation
Represents a conversation between a buyer and seller regarding a specific car.

### Message
Individual messages within a conversation.

### SellerReview
Reviews given to sellers by buyers who have interacted with them.

### SellerRequest
Requests from users to become sellers.

### ChatbotSession and ChatbotMessage
Tracks user interactions with the chatbot assistant.
```

## Database Schema Information

This ER diagram captures the main entities and relationships in the Dongelek car marketplace system. The database schema is designed to support:

1. User management (buyers and sellers)
2. Car listing management
3. Location-based filtering
4. Messaging between users
5. Favoriting and comparing cars
6. Rating and reviewing sellers
7. Seller application process
8. AI chatbot assistance
