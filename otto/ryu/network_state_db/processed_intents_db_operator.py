
from datetime import datetime, timedelta
from pymongo import MongoClient
from exceptions import ProcessedIntentsDbException

class ProcessedIntentsDbOperator:

      __instance = None

      @staticmethod
      def get_instance():
          if ProcessedIntentsDbOperator.__instance is None:
             ProcessedIntentsDbOperator()
          return ProcessedIntentsDbOperator.__instance

      def __init__(self):
          if ProcessedIntentsDbOperator.__instance is None:
             self.mongo_connector = MongoClient('localhost', 27018)
             self.database = self.mongo_connector['intent_history']
             self.collection = self.database['processed_intents']

             ProcessedIntentsDbOperator.__instance = self

          else:
            raise Exception(f"An occurence of ProcessedIntentsDbOperator exists at {ProcessedIntentsDbOperator.__instance}")

      def save_intent(self, intent:str, context:str, operations:list[str], timestamp) -> dict:
            processed_intent = {
                "declaredBy": context,
                "intent": intent,
                "outcome": operations,
                "timestamp": timestamp
            }
            try:

               self.collection.insert_one(processed_intent)

            except PyMongoError as e:
                   raise ProcessedIntentsDbException(
                   f"Error while putting processed_intent into otto_processed_intents_db: {e}")

            print(processed_intent)
            return processed_intent


      def get_latest_activity(self) -> dict:
            timestamp = datetime.now() - timedelta(hours=24)
            """
            query = {
                  '$expr': { '$gt': ["$timestamp", timestamp] }
            }
            """
            try:

               latest_data = self.collection.find().sort('_id', -1).limit(5)

               response = {}

               for record in latest_data:
                   print(f"RECORD {record}")
                   response[str(record['timestamp'])] = {}
                   response[str(record['timestamp'])]['declaredBy'] = record['declaredBy']
                   response[str(record['timestamp'])]['intent'] = record['intent']
                   response[str(record['timestamp'])]['outcome'] = record['outcome']


            except PyMongoError as e:
                   raise ProcessedIntentsDbException(
                   f"Error while attempting to achieve latest data: {e}")

            return response

      def get_weekly_activity(self) -> dict:
        today = datetime.today()
        one_week_ago = today - timedelta(weeks=1)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": one_week_ago, "$lt": today}
                }
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}]

        response = {}

        results = list(self.collection.aggregate(pipeline))

        for result in results:
            response[result['_id']] = result['count']
 
        return response


      def get_top_activity(self) -> dict:

        pipeline = [
            {
                "$group": {
                    "_id": "$declaredBy", "count": {"$sum": 1}}
            },  
            {"$sort": {"count": -1}}]

        response = {}

        results = list(self.collection.aggregate(pipeline))

        for result in results:
            response[result['_id']] = result['count']
 
        return response

