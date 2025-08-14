# Rooms API Documentation

## Overview

The Rooms API handles room management operations for vendors. It allows vendors to create, update, delete, and list their rooms. This API is specifically designed for vendor operations and requires vendor authentication.

## Base URL
```
/rooms/
```

## Models

### Room Model
The main room model that stores all room information.

```python
class Room(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rooms')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='rooms', blank=True, null=True)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.IntegerField()
    google_map_url = models.URLField(blank=True, null=True, verbose_name="Google Maps URL", max_length=400)
    image = models.ImageField(upload_to='room_images/')
    image2 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg')
    image3 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg')
    image4 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg', blank=True, null=True)
    image5 = models.ImageField(upload_to='room_images/', default='https://example.com/default_image.jpg', blank=True, null=True)
    availability = models.BooleanField(default=True)
    pet_allowed = models.BooleanField(default=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, blank=True, null=True)
    bed_type = models.ForeignKey(BedType, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
```

**Validation Rules:**
- At least 3 images are required (image, image2, image3 must be provided)
- Maximum occupancy must be a positive integer
- Price per night must be a positive decimal

**Methods:**
- `get_average_rating()`: Returns the average rating for the room
- `get_absolute_url()`: Returns the URL for room detail view

### Location Model
Stores location information for rooms.

```python
class Location(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
```

### City Model
Stores city information.

```python
class City(models.Model):
    name = models.CharField(max_length=50, unique=True)
```

### Country Model
Stores country information.

```python
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
```

### Category Model
Room categories (Hotel, Apartment, Villa, etc.).

```python
class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images/', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_categories', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### RoomType Model
Types of rooms (Single, Double, Suite, etc.).

```python
class RoomType(models.Model):
    name = models.CharField(max_length=50)
```

### BedType Model
Types of beds (Single, Double, King Size, etc.).

```python
class BedType(models.Model):
    name = models.CharField(max_length=50)
```

### Amenity Model
Room amenities (WiFi, AC, TV, etc.).

```python
class Amenity(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='amenity_images/', blank=True)
```

## Authentication

All rooms API endpoints require vendor authentication:

**Headers:**
```
Authorization: Bearer <access_token>
```

**Permission:** User must have `is_vendor=True` in their profile.

## API Endpoints

### Create Room
**POST** `/rooms/create/`

Create a new room listing. Only vendors can create rooms.

**Headers:**
```
Authorization: Bearer <vendor_access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "name": "Luxury Ocean View Suite",
    "description": "A beautiful luxury suite with stunning ocean views and modern amenities",
    "price_per_night": "8500.00",
    "max_occupancy": 4,
    "google_map_url": "https://maps.google.com/maps?q=location",
    "location": 1,
    "category": 1,
    "room_type": 1,
    "bed_type": 1,
    "availability": true,
    "pet_allowed": true,
    "amenities": [1, 2, 3, 4],
    "image": "file_upload",
    "image2": "file_upload",
    "image3": "file_upload",
    "image4": "file_upload",
    "image5": "file_upload"
}
```

**Required Fields:**
- `name`: Room name
- `description`: Room description
- `price_per_night`: Price per night (decimal)
- `max_occupancy`: Maximum number of guests
- `location`: Location ID
- `image`: Primary image file
- `image2`: Secondary image file
- `image3`: Third image file

**Optional Fields:**
- `google_map_url`: Google Maps URL for location
- `category`: Category ID
- `room_type`: Room type ID
- `bed_type`: Bed type ID
- `availability`: Room availability (default: true)
- `pet_allowed`: Whether pets are allowed (default: true)
- `amenities`: Array of amenity IDs
- `image4`: Fourth image file
- `image5`: Fifth image file

**Response:**
```json
{
    "id": 1,
    "name": "Luxury Ocean View Suite",
    "description": "A beautiful luxury suite with stunning ocean views and modern amenities",
    "location": {
        "name": "Mumbai Central",
        "city_name": "Mumbai",
        "country_name": "India"
    },
    "category": {
        "id": 1,
        "name": "Hotel",
        "image": "/images/category_images/hotel.jpg"
    },
    "price_per_night": "8500.00",
    "max_occupancy": 4,
    "google_map_url": "https://maps.google.com/maps?q=location",
    "image": "/images/room_images/room1.jpg",
    "image2": "/images/room_images/room1_2.jpg",
    "image3": "/images/room_images/room1_3.jpg",
    "image4": "/images/room_images/room1_4.jpg",
    "image5": "/images/room_images/room1_5.jpg",
    "availability": true,
    "pet_allowed": true,
    "room_type": {
        "id": 1,
        "name": "Suite"
    },
    "bed_type": {
        "id": 1,
        "name": "King Size"
    },
    "amenities": [
        {
            "id": 1,
            "name": "WiFi",
            "image": "/images/amenity_images/wifi.jpg"
        },
        {
            "id": 2,
            "name": "Air Conditioning",
            "image": "/images/amenity_images/ac.jpg"
        }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "average_rating": null
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/rooms/create/ \
  -H "Authorization: Bearer <vendor_token>" \
  -F "name=Luxury Ocean View Suite" \
  -F "description=A beautiful luxury suite with stunning ocean views" \
  -F "price_per_night=8500.00" \
  -F "max_occupancy=4" \
  -F "location=1" \
  -F "category=1" \
  -F "room_type=1" \
  -F "bed_type=1" \
  -F "amenities=1,2,3" \
  -F "image=@room1.jpg" \
  -F "image2=@room1_2.jpg" \
  -F "image3=@room1_3.jpg"
```

### Get Room Details
**GET** `/rooms/edit/{room_id}/`

Get detailed information about a specific room. Vendors can view any room details.

**Headers:**
```
Authorization: Bearer <vendor_access_token>
```

**Response:**
```json
{
    "id": 1,
    "name": "Luxury Ocean View Suite",
    "description": "A beautiful luxury suite with stunning ocean views and modern amenities",
    "location": {
        "name": "Mumbai Central",
        "city_name": "Mumbai",
        "country_name": "India"
    },
    "category": {
        "id": 1,
        "name": "Hotel",
        "image": "/images/category_images/hotel.jpg"
    },
    "price_per_night": "8500.00",
    "max_occupancy": 4,
    "google_map_url": "https://maps.google.com/maps?q=location",
    "image": "/images/room_images/room1.jpg",
    "image2": "/images/room_images/room1_2.jpg",
    "image3": "/images/room_images/room1_3.jpg",
    "image4": "/images/room_images/room1_4.jpg",
    "image5": "/images/room_images/room1_5.jpg",
    "availability": true,
    "pet_allowed": true,
    "room_type": {
        "id": 1,
        "name": "Suite"
    },
    "bed_type": {
        "id": 1,
        "name": "King Size"
    },
    "amenities": [
        {
            "id": 1,
            "name": "WiFi",
            "image": "/images/amenity_images/wifi.jpg"
        }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "average_rating": 4.5
}
```

### Update Room
**PUT** `/rooms/edit/{room_id}/`

Update an existing room. Partial updates are supported.

**Headers:**
```
Authorization: Bearer <vendor_access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```json
{
    "name": "Updated Luxury Suite",
    "description": "Updated description with new amenities",
    "price_per_night": "9000.00",
    "availability": false
}
```

**Response:** Same structure as room creation response with updated data.

**Example cURL:**
```bash
curl -X PUT http://localhost:8000/rooms/edit/1/ \
  -H "Authorization: Bearer <vendor_token>" \
  -F "name=Updated Luxury Suite" \
  -F "price_per_night=9000.00" \
  -F "availability=false"
```

### Delete Room
**DELETE** `/rooms/edit/{room_id}/`

Delete a room listing.

**Headers:**
```
Authorization: Bearer <vendor_access_token>
```

**Response:**
```json
{
    "message": "DELETE_SUCCESS Luxury Ocean View Suite."
}
```

**HTTP Status:** 204 No Content

### Get Vendor's Rooms
**GET** `/rooms/vendor/rooms/`

Get all rooms created by the authenticated vendor.

**Headers:**
```
Authorization: Bearer <vendor_access_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Luxury Ocean View Suite",
        "description": "A beautiful luxury suite with stunning ocean views",
        "location": {
            "name": "Mumbai Central",
            "city_name": "Mumbai",
            "country_name": "India"
        },
        "category": {
            "id": 1,
            "name": "Hotel",
            "image": "/images/category_images/hotel.jpg"
        },
        "price_per_night": "8500.00",
        "max_occupancy": 4,
        "image": "/images/room_images/room1.jpg",
        "availability": true,
        "created_at": "2024-01-01T00:00:00Z",
        "average_rating": 4.5
    },
    {
        "id": 2,
        "name": "Cozy Mountain Cabin",
        "description": "A peaceful cabin in the mountains",
        "location": {
            "name": "Shimla Hills",
            "city_name": "Shimla",
            "country_name": "India"
        },
        "price_per_night": "3500.00",
        "max_occupancy": 2,
        "image": "/images/room_images/cabin1.jpg",
        "availability": true,
        "created_at": "2024-01-02T00:00:00Z",
        "average_rating": 4.2
    }
]
```

## Serializers

### RoomSerializer
Main serializer for room operations.

**Fields:**
- `id`: Room ID (read-only)
- `name`: Room name
- `description`: Room description
- `location`: Location details (nested)
- `category`: Category details (nested)
- `price_per_night`: Price per night
- `max_occupancy`: Maximum occupancy
- `google_map_url`: Google Maps URL
- `image`, `image2`, `image3`, `image4`, `image5`: Room images
- `availability`: Room availability
- `pet_allowed`: Pet allowance
- `room_type`: Room type details (nested)
- `bed_type`: Bed type details (nested)
- `amenities`: Amenities list (nested)
- `created_at`: Creation timestamp (read-only)
- `average_rating`: Average rating (read-only)

### LocationSerializer
Serializer for location information.

**Fields:**
- `name`: Location name
- `city_name`: City name (read-only)
- `country_name`: Country name (read-only)

### CategorySerializer
Serializer for room categories.

**Fields:**
- `id`: Category ID
- `name`: Category name
- `image`: Category image

### AmenitySerializer
Serializer for room amenities.

**Fields:**
- `id`: Amenity ID
- `name`: Amenity name
- `image`: Amenity image

### RoomTypeSerializer & BedTypeSerializer
Simple serializers for room and bed types.

**Fields:**
- `id`: Type ID
- `name`: Type name

## Error Handling

### Common Error Responses

#### 400 Bad Request - Validation Error
```json
{
    "name": ["This field is required."],
    "price_per_night": ["Ensure this value is greater than 0."],
    "image": ["No file was submitted."]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden - Not a Vendor
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found - Room Not Found
```json
{
    "detail": "Room not found."
}
```

#### 413 Payload Too Large - File Size Limit
```json
{
    "image": ["File size too large. Maximum size allowed is 5MB."]
}
```

## File Upload Guidelines

### Image Upload Requirements

1. **Supported Formats:** JPEG, PNG, WebP
2. **Maximum File Size:** 5MB per image
3. **Recommended Dimensions:** 1200x800 pixels
4. **Required Images:** At least 3 images (image, image2, image3)
5. **Optional Images:** image4, image5

### Image Validation

```python
def clean(self):
    super().clean()
    # Ensure at least three image fields are populated
    images = [self.image, self.image2, self.image3, self.image4, self.image5]
    filled_images = [img for img in images if img]
    if len(filled_images) < 3:
        raise ValidationError('At least three images are required.')
```

## Business Rules

1. **Vendor-Only Access:** Only users with `is_vendor=True` can access rooms endpoints
2. **Room Ownership:** Vendors can only edit/delete rooms they created
3. **Image Requirements:** Minimum 3 images required for room creation
4. **Price Validation:** Price per night must be positive
5. **Occupancy Validation:** Max occupancy must be positive integer
6. **Availability Control:** Vendors can enable/disable room availability

## Integration Notes

### With Accounts App
- Room bookings are handled in the accounts app (`/accounts/reservations/`)
- Room search and public listing is handled in accounts app (`/accounts/room-search/`)
- User wishlists are managed in accounts app

### With Admin Portal
- Admin can view all rooms via admin portal endpoints
- Categories, amenities, locations are managed by admin
- Room types and bed types are configured by admin

### With Vendor Management
- Vendor dashboard shows room statistics
- Vendor bookings and earnings are tracked
- Room performance analytics available

## Real-time Features

Room availability updates can be broadcasted using WebSocket connections for real-time inventory management.

## Caching Strategy

Room data is cached to improve performance:
- Room details cached for 1 hour
- Room listings cached for 30 minutes
- Search results cached based on query parameters

## Security Considerations

1. **Authentication Required:** All endpoints require valid vendor tokens
2. **File Upload Security:** Images are validated for type and size
3. **Input Validation:** All input fields are validated and sanitized
4. **Rate Limiting:** File uploads may be rate-limited
5. **CORS Policy:** Configured for frontend domain access