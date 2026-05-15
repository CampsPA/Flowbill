# Creates global exceptions classes to handle errors, allows for domain exceptions 
# to be raised instead of raw HTTP exceptions
# These exceptions are specific for the business logic.

# Here we write the definition -  the bluprint side of the custom fuctions.
# The caller side will replace all the HTTP exceptions in the service.py files (refactoring)
# Then the Handler that catches the exceptions goes into main.py


# Custom error handling for missing data, takes resource name and id as parameters
class ResourceNotFound(Exception): # HTTP 404
    """Raised when a specific resource is not found."""
    def __init__(self, resource, id):
        self.message = f"Resource {resource} with {id} not found"
        super().__init__(self.message)
    


# Custom error handling for existing data, takes field and value as parameters
class DuplicateRecord(Exception): # HTTP 400/409
    """Raised when duplicated data is submitted."""
    def __init__(self, field, value):
        self.message = f"{field} '{value}' is already registered."
        super().__init__(self.message)



# Custom error handling for external service call error, takes service and reason as parameters
class ExternalServiceError(Exception): # HTTP 502
    """Raised for external service error handling."""
    def __init__(self, service, reason):
        self.message = f"An error occurred calling service {service} due to {reason}."
        super().__init__(self.message)




# Custom error handling for unauthorized resource access, takes user and resource
class PermissionDeniedError(Exception): # HTTP 403
    """Raised due to unauthorized access."""
    def __init__(self, user, resource):
        self.message = f"Access unauthorized for user {user} for {resource}."
        super().__init__(self.message)

