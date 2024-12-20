import requests

https://www.pathofexile.com/api/trade2/search/Standard
{
    "query": {
        "status": {
            "option": "online"
        },
        "name": "The Pariah",
        "type": "Unset Ring",
        "stats": [{
            "type": "and",
            "filters": []
        }]
    },
    "sort": {
        "price": "asc"
    }
}