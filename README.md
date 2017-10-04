# courex-assignment
Use Github API to retrieve users from Singapore

Github provide two ways to do this:
- Using REST API, to get all users, then filter based on their location
    - get a list of users: https://api.github.com/users
    - for each user returned:
        - call another API to get detail: https://api.github.com/users/mojombo
        - then check if location is Singapore
    - use paging info in response header to get next batch of users

    - advantages: flexible, can filter based on other info, or based on similar match instead of exact match...
    - disadvantages: slow, need to invoke API a lot, so easily reached request limit

- Using search API

    https://api.github.com/search/users?q=location%3Asingapore
    
    This will return all user with location Singapore, however, Github limit the number of result to 1000, while there are over 11k users.

    So we need to search multiple times, each time search for user created within a period (6 months)

I'll use the search API for this assignment
