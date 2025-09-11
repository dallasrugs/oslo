# file: console-api/routers/supabase.py
# maybe consider using a subdirectory for supabase itself in future (not so far in future)
'''
 TODO: 
    Migrate raise HTTPException to JSONException for detailed response [Ongoing]
    Prepare methods for updating, deleting Items [Ongoing]
    Refine error and exception handling strategies
'''
import sqlalchemy as db
from sqlalchemy import func, distinct
from fastapi import HTTPException
from internal import status as connection # load connection details from database status 
from datetime import datetime
from internal.logger import logger 
from internal.utilities import ImageUploader
from internal.templates import Messages
from internal.connector import getSupabase
import json 

class Supabase:
    def __init__(self):
        self._connect()

    def _connect(self):
        try:
            self.engine = connection.db_engine
            self.metadata = connection.db_metadata
            self.session = connection.db_session

            # Define tables, find a way to import Schema correctly and then ask
            self.schema = getSupabase()
            self.Category = self.metadata.tables[f'{self.schema}.Category']
            self.Subcategory = self.metadata.tables[f'{self.schema}.Subcategory']
            self.Items = self.metadata.tables[f'{self.schema}.Item']
            self.ItemCategory = self.metadata.tables[f'{self.schema}.ItemCategory']
            self.ItemImage = self.metadata.tables[f'{self.schema}.ItemImage']

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

    def _retry_on_failure(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._connect()  # reconnect
            try:
                return func(*args, **kwargs)  # retry
            except Exception as e2:
                raise HTTPException(status_code=500, detail=f"Database error after reconnect: {str(e2)}")

    def count_categories(self, filter_str="{}"):
            try:
                filter_dict = json.loads(filter_str)

                # Base statement for counting
                count_stmt = db.select(func.count()).select_from(self.Category)

                # Apply filters (same logic as in the categories method)
                for key, value in filter_dict.items():
                    if hasattr(self.Category.c, key):
                        column = getattr(self.Category.c, key)
                        if isinstance(value, list):
                            if all(isinstance(v, str) for v in value) or all(isinstance(v, int) for v in value):
                                count_stmt = count_stmt.where(column.in_(value))
                            else:
                                raise ValueError(f"Incompatible filter list type for field '{key}' in count_categories")
                        elif isinstance(value, str):
                            count_stmt = count_stmt.where(column.ilike(f"%{value}%"))
                        else:
                            count_stmt = count_stmt.where(column == value)

                total_count = self.session.execute(count_stmt).scalar_one()
                return total_count

            except Exception as e:
                # Log the error, but perhaps don't raise HTTPException here
                # just return 0 or re-raise if you want the API call to fail
                logger.error(f"Error Origin: supabase.py/count_categories \n {str(e)}")
                # Depending on how critical this is, you might return 0
                # or re-raise if total count failure should error the whole request.
                raise # Re-raise if you want it to propagate to the router's error handler

        
    async def categories(self, filter_str="{}", range_str="[0,24]", sort_str='["id","DESC"]'):
        try:
            filter_dict = json.loads(filter_str)
            range_list = json.loads(range_str)
            sort_list = json.loads(sort_str)

            stmt = db.select(
                self.Category.c.id,
                self.Category.c.name,
                self.Category.c.description,
                self.Category.c.created_at
            )

            # Safely apply filters
            for key, value in filter_dict.items():
                if hasattr(self.Category.c, key):
                    column = getattr(self.Category.c, key)

                    if isinstance(value, list):
                        # Check type of list elements and apply correct filter
                        if all(isinstance(v, str) for v in value):
                            stmt = stmt.where(column.in_(value))
                        elif all(isinstance(v, int) for v in value):
                            stmt = stmt.where(column.in_(value))
                        else:
                            raise ValueError(f"Incompatible filter list type for field '{key}'")
                    elif isinstance(value, str):
                        stmt = stmt.where(column.ilike(f"%{value}%"))
                    else:
                        stmt = stmt.where(column == value)

            # Sorting
            sort_field, sort_order = sort_list
            if hasattr(self.Category.c, sort_field):
                sort_col = getattr(self.Category.c, sort_field)
                if sort_order.upper() == "ASC":
                    stmt = stmt.order_by(sort_col.asc())
                else:
                    stmt = stmt.order_by(sort_col.desc())

            # Pagination
            start, end = range_list
            limit = end - start + 1
            stmt = stmt.offset(start).limit(limit)

            results = self.session.execute(stmt).mappings().all()
            return results

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error Origin: supabase.py/categories \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    async def categories(self, filter_str="{}", range_str="[0,24]", sort_str='["id","DESC"]'):
        try:
            filter_dict = json.loads(filter_str)
            range_list = json.loads(range_str)
            sort_list = json.loads(sort_str)

            stmt = db.select(
                self.Category.c.id,
                self.Category.c.name,
                self.Category.c.description,
                self.Category.c.created_at
            )

            # Safely apply filters
            for key, value in filter_dict.items():
                if hasattr(self.Category.c, key):
                    column = getattr(self.Category.c, key)

                    if isinstance(value, list):
                        # Check type of list elements and apply correct filter
                        if all(isinstance(v, str) for v in value):
                            stmt = stmt.where(column.in_(value))
                        elif all(isinstance(v, int) for v in value):
                            stmt = stmt.where(column.in_(value))
                        else:
                            raise ValueError(f"Incompatible filter list type for field '{key}'")
                    elif isinstance(value, str):
                        stmt = stmt.where(column.ilike(f"%{value}%"))
                    else:
                        stmt = stmt.where(column == value)

            # Sorting
            sort_field, sort_order = sort_list
            if hasattr(self.Category.c, sort_field):
                sort_col = getattr(self.Category.c, sort_field)
                if sort_order.upper() == "ASC":
                    stmt = stmt.order_by(sort_col.asc())
                else:
                    stmt = stmt.order_by(sort_col.desc())

            # Pagination
            start, end = range_list
            limit = end - start + 1
            stmt = stmt.offset(start).limit(limit)

            results = self.session.execute(stmt).mappings().all()
            return results

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error Origin: supabase.py/categories \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    

    async def items(self, filter_str="{}", range_str="[0,9]", sort_str='["id","ASC"]'):
        try:
            # Parse query params
            filter_dict = json.loads(filter_str)
            range_list = json.loads(range_str)
            sort_list = json.loads(sort_str)

            # Base query with joins and aggregation
            # We select all columns from Items, plus aggregated category name and MIN of image URL
            stmt = db.select(
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                # Use func.min or func.max if an item can have multiple categories
                # and you only want one, or ensure unique category per item in join
                func.min(self.Category.c.name).label("category"), # <-- Use MIN/MAX for category name if it might duplicate
                func.min(self.ItemImage.c.url).label("url") # <-- Fix: Use aggregate function for URL
            ).join( # Use join where necessary, outerjoin if items can exist without category/image
                self.ItemCategory, self.Items.c.id == self.ItemCategory.c.itemId
            ).join(
                self.Category, self.Category.c.id == self.ItemCategory.c.categoryId
            ).join(
                self.ItemImage, self.Items.c.id == self.ItemImage.c.itemId
            ).group_by( # <-- Crucial: Group by all non-aggregated columns from Items
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                # You must group by Category.c.name if it's not aggregated
                # Or ensure your schema ensures one category per item for this query
                # If an item can have multiple categories, this will still produce multiple rows.
                # If that's the case, you might need to rethink category selection here.
            )
            
            # Re-evaluate the grouping. If an Item has a unique Category via ItemCategory,
            # and you just want that one category name, you can group by it.
            # Otherwise, you might need to get categories separately or aggregate them.
            # For a 1-to-1 or 1-to-many where you pick one, group by:
            stmt = stmt.group_by(self.Items.c.id, self.Items.c.title, self.Items.c.description, self.Category.c.name)
            
            # Filtering (simple equality) - apply to the grouped result if filtering by item attributes
            for key, value in filter_dict.items():
                if hasattr(self.Items.c, key):
                    stmt = stmt.where(getattr(self.Items.c, key) == value)

            # Sorting - apply to the grouped results
            sort_field, sort_order = sort_list
            if hasattr(self.Items.c, sort_field):
                sort_col = getattr(self.Items.c, sort_field)
                if sort_order.upper() == "ASC":
                    stmt = stmt.order_by(sort_col.asc())
                else:
                    stmt = stmt.order_by(sort_col.desc())
            else: # If sorting by category, you need to use the aliased column
                 if sort_field == "category":
                     sort_col = self.Category.c.name # Or the alias from the select
                     if sort_order.upper() == "ASC":
                         stmt = stmt.order_by(sort_col.asc())
                     else:
                         stmt = stmt.order_by(sort_col.desc())
                 # Add similar logic for 'url' if sorting by it
            
            # Pagination
            # Pagination must happen *after* grouping
            start, end = range_list
            limit = end - start + 1
            stmt = stmt.offset(start).limit(limit)

            results = self.session.execute(stmt).mappings().all()
            return results

        except Exception as e:
            self.session.rollback()  # Rollback the transaction on error
            logger.error(f"Error Origin: supabase.py/items \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    async def allItems(self):
        try:
            # Base query with joins and aggregation
            stmt = db.select(
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                func.min(self.Category.c.name).label("category"),  # pick one category per item
                func.min(self.ItemImage.c.url).label("url"),      # pick one image per item
                self.Items.c.item_importance_score,               # additional field
                self.Items.c.item_identifier                       # additional field
            ).join(
                self.ItemCategory, self.Items.c.id == self.ItemCategory.c.itemId
            ).join(
                self.Category, self.Category.c.id == self.ItemCategory.c.categoryId
            ).join(
                self.ItemImage, self.Items.c.id == self.ItemImage.c.itemId
            ).group_by(
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                self.Items.c.item_importance_score,
                self.Items.c.item_identifier,
                self.Category.c.name
            )

            results = self.session.execute(stmt).mappings().all()
            return results

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error Origin: supabase.py/items \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


    
    def getItembyID(self, id):
        try:
            results = self.getItems(id)
            return results
        except Exception as e: 
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    async def getCategoryByID(self, category_id):
        try:
            stmt = db.select(self.Category).where(self.Category.c.id == category_id)
            results = self.session.execute(stmt).mappings().all()
            return results

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
        

    async def getSubcategoryByID(self, category_id: int, subcategory_id: int):
        try:
            stmt = db.select(self.Subcategory).where(
                (self.Subcategory.c.id == subcategory_id) &
                (self.Subcategory.c.category_id == category_id)
            )
            result = self.session.execute(stmt).mappings().first()
            return dict(result) if result else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    '''
    Features: Individual Add, Bulk Add
    '''
    async def addCategory(self, name, desc):
        '''
            Adding new category by adding the last inserted ID 
        '''
        try:
            id_ = await self.getLastID(self.Category)  # getLastID must also be async
            created_at_ = datetime.now()
            query = db.insert(self.Category).values(
                id=id_,
                created_at = created_at_,
                name = name,
                description = desc
            )
            self.session.execute(query)
            self.session.commit()
            return f"{name} Category Added"
        
        except Exception as e:
            logger.error(f"Error Origin: supabase.py/addCategory \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    async def addSubcategory(self, category_id: int, name: str, desc: str):
        """
        Add a new subcategory under an existing category.
        """
        try:
            # 1. Check if the category exists
            query = db.select(self.Category).where(self.Category.c.id == category_id)
            result = self.session.execute(query).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

            # 2. Get the last ID for subcategories
            id_ = await self.getLastID(self.Subcategory)
            created_at_ = datetime.now()

            # 3. Build slug (optional, simple lower + replace)
            slug = name.lower().replace(" ", "-")

            # 4. Insert into Subcategory table
            query = self.Subcategory.insert().values(
                id=id_,
                created_at=created_at_,
                name=name,
                description=desc,
                slug=slug,
                category_id=category_id
            )

            self.session.execute(query)
            self.session.commit()

            return {"message": f"Subcategory '{name}' added under Category {category_id}"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error Origin: supabase.py/addSubcategory \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    def updateCategory(self,category_id,name,desc):
        '''
            Updates category by its ID, Warning: updates the row even if the input is empty
        '''
        # check if category exists
        try:
            if self.getCategoryByID(category_id) is not None:
                created_at_ = datetime.now()

                query = db.update(self.Category).values(
                    created_at = created_at_,
                    name=name,
                    description=desc 
                ).where(
                    self.Category.c.id == category_id
                )

                self.session.execute(query)
                self.session.commit()
                return f"{name} Category Updated."
            else:
                return "Category does not exist, if it does not exist add"

        except Exception as e:
            logger.error(f"Error Origin: supabase.py/updateCategory \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    def updateSubcategory(self, category_id: int, subcategory_id: int, name: str, desc: str):
        """
        Update subcategory by ID under a given category.
        """
        try:
            # 1. Check if category exists
            category = self.getCategoryByID(category_id)
            if category is None:
                raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

            # 2. Check if subcategory exists under this category
            query = db.select(self.Subcategory).where(
                (self.Subcategory.c.id == subcategory_id) &
                (self.Subcategory.c.category_id == category_id)
            )
            result = self.session.execute(query).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail=f"Subcategory {subcategory_id} not found in Category {category_id}")

            # 3. Update subcategory
            created_at_ = datetime.now()
            slug = name.lower().replace(" ", "-")

            update_query = (
                db.update(self.Subcategory)
                .values(
                    created_at=created_at_,
                    name=name,
                    description=desc,
                    slug=slug
                )
                .where(
                    (self.Subcategory.c.id == subcategory_id) &
                    (self.Subcategory.c.category_id == category_id)
                )
            )

            self.session.execute(update_query)
            self.session.commit()

            return {"message": f"Subcategory {subcategory_id} updated in Category {category_id}"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error Origin: supabase.py/updateSubcategory \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    

    def deleteCategory(self,category_id):
        '''
            Deletes a category based on category id 
        '''
        try:
            if self.getCategoryByID(category_id) is not None:
                query = db.delete(self.Category).where(
                    self.Category.c.id == category_id
                )

                self.session.execute(query)
                self.session.commit()
                return f"Category Deleted Successfully."
            else:
                return "Category does not exist, if it does not exist add"
            
        except Exception as e:
            logger.error(f"Error Origin: supabase.py/updateCategory \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    def deleteSubcategory(self, category_id: int, subcategory_id: int):
        """
        Deletes a subcategory by ID under a given category.
        """
        try:
            # 1. Check if category exists
            category = self.getCategoryByID(category_id)
            if category is None:
                raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

            # 2. Check if subcategory exists under this category
            query = db.select(self.Subcategory).where(
                (self.Subcategory.c.id == subcategory_id) &
                (self.Subcategory.c.category_id == category_id)
            )
            result = self.session.execute(query).fetchone()

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Subcategory {subcategory_id} not found in Category {category_id}"
                )

            # 3. Delete subcategory
            delete_query = db.delete(self.Subcategory).where(
                (self.Subcategory.c.id == subcategory_id) &
                (self.Subcategory.c.category_id == category_id)
            )

            self.session.execute(delete_query)
            self.session.commit()

            return {"message": f"Subcategory {subcategory_id} deleted from Category {category_id}"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error Origin: supabase.py/deleteSubcategory \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    
    async def addNewItem(self,title,desc,categoryID):
        '''
            Add new Item to Supabase Database
        '''
        try:
            # Part 1: Add Record to Item First
            id_ = await self.getLastID(self.Items)+1 # getLastID must also be async
            created_at_ = datetime.now()
            query1 = db.insert(self.Items).values(
                id=id_,
                created_at = created_at_,
                title = title,
                description = desc
            )
            self.session.execute(query1)

            # Part 2: Add Item to Category Mapper
            created_at_ = datetime.now()
            query1 = db.insert(self.ItemCategory).values(
                itemId=id_,
                categoryId=categoryID,
                created_at = created_at_
            )
            self.session.execute(query1)
            self.session.commit()

            try:
                updated_item_db_object = self.getItemNoImage(id_)[0]
                return updated_item_db_object
            
            except Exception as e: 
                logger.error(f"Error Origin: supabase.py/addNewItem \n {str(e)}")
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error Origin: supabase.py/addNewItem \n {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    async def DeleteItembyID(self, item_id):
        '''
            Delete an item and all its references in related tables.
        '''
        try:
            # Delete from ItemCategory first
            query_itemcategory = db.delete(self.ItemCategory).where(
                self.ItemCategory.c.itemId == item_id
            )
            self.session.execute(query_itemcategory)

            # Delete from ItemImage (if you have images linked to the item)
            query_itemimage = db.delete(self.ItemImage).where(
                self.ItemImage.c.itemId == item_id
            )
            self.session.execute(query_itemimage)

            # Now delete from Items
            query_item = db.delete(self.Items).where(
                self.Items.c.id == item_id
            )
            self.session.execute(query_item)

            self.session.commit()
            return Messages.success(f"Item Deleted Successfully.")

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error Origin: supabase.py/DeleteItembyID \n {str(e)}")
            return Messages.exception_message(
                origin="supabase.py/DeleteItembyID",
                message="Item was not deleted successfully, please check exception message",
                exception=e
            )
    async def UpdateItem(self, item_id,title = None ,desc = None ,categoryID = None):
        '''
            Update Items from Console
        '''
        try:
            if self.checkIdExists(self.Items, item_id):
                # part 0: get previous values, compare (if change needed update that)
                items = self.getItems(item_id)[0]

                # if empty then update, old values
                if  desc == None:
                    desc = items.description

                if  title == None:
                    title = items.title 
                
                if categoryID == None:
                    categoryID = items.category_id
                 
                # part 1: update item table
                query = db.update(self.Items).values(
                    title = title,
                    description = desc, 
                    created_at = datetime.now()
                ).where(self.Items.c.id == item_id)
                self.session.execute(query)

                # part 2: update item category table 
                query_2 = db.update(self.ItemCategory).values(categoryId = categoryID).where(self.ItemCategory.c.itemId == item_id)
                self.session.execute(query_2)
                # commit/flush entries
                self.session.commit()
                updated_item_db_object = await self.getItemsOnly(item_id)[0]
                # If it's a SQLAlchemy Row, convert it to dict
                if hasattr(updated_item_db_object, '_asdict'):
                    updated_item_db_object = updated_item_db_object._asdict()
                elif not isinstance(updated_item_db_object, dict):
                    updated_item_db_object = dict(updated_item_db_object)

            return updated_item_db_object
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error Origin: supabase.py/UpdateItem \n {str(e)}")
            return Messages.exception_message(
                origin="supabase.py/UpdateItem",
                message="Item was not updated successfully, please check exception message",
                exception=e
            )

    async def UpdateItemImage(self, item_id, temp_file_path):
        try:
            image_filename = f"{item_id}.jpg"
            response = await ImageUploader(temp_file_path, image_filename)
            if response.status_code == 200:

                # Part 4: Add URL to ItemImage 
                imageid_ = await self.getLastID(self.ItemImage)  # getLastID must also be async
                created_at_ = datetime.now()
                query = db.insert(self.ItemImage).values(
                    id=imageid_,
                    created_at = created_at_,
                    itemId = item_id,
                    url = f"https://mcaniisezxryajilvjdb.supabase.co/storage/v1/object/public/item-images/{image_filename}",
                    altText = "Updated via Oslo FE"
                )
                self.session.execute(query)
                self.session.commit()
                return Messages.success(message=f"Image updated successfully")
        except Exception as e:
            logger.error(f"Exception has occured. Check Exception: \n {e}")

            return Messages.exception_message(
                message=f"Image was not updated, please check for exceptions",
                origin="routers/supabase.py/UpdateItemImage.py",
                exception= e, 
                status_code=500
            )


    ## Utility Functions
    # use it to retrieve last id inserted to given table
    async def getLastID(self, table):
        try:
            query = db.select(db.func.max(table.c.id))
            result = self.session.execute(query).scalar()
            return (result or 0) + 1
        except Exception as e:
            logger.error("Error Origin: supabase.py/getLastID %s", e)
            raise HTTPException(status_code=500, detail=f"Error getting last ID: {str(e)}")
    
    async def checkIdExists(self, table, id):
        try:
            query = db.select(table).where(table.c.id == id)
            result = self.session.execute(query)
            return True if list(result).len() else False
        except Exception as e:
            logger.error("Error Origin: supabase.py/checkIdExists %s", e)
            raise HTTPException(status_code=500, detail=f"Error supabase.py/checkIdExists : {str(e)}")            


    # this is for returning item details 
    def getItems(self,item_id):
        try:
            stmt = db.select(
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                self.Category.c.id.label("category_id"),
                self.Category.c.name,
                self.ItemImage.c.url
                             ).where(
                (self.Items.c.id == self.ItemCategory.c.itemId) &
                (self.Category.c.id == self.ItemCategory.c.categoryId) & 
                (self.ItemImage.c.itemId == self.Items.c.id) & 
                (self.Items.c.id == item_id))
            results = self.session.execute(stmt).mappings().all()
            return results 

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    async def getItemsOnly(self,item_id):
        try:
            stmt = db.select(
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                self.ItemCategory.c.categoryId.label("category_id"),
                self.ItemImage.c.url).where(
                    (self.Items.c.id == item_id) & 
                    (self.ItemImage.c.itemId == self.Items.c.id) & 
                    (self.ItemCategory.c.itemId == item_id))
            results = self.session.execute(stmt).mappings().all()
            return results 

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def getItemNoImage(self,item_id):
        try:
            stmt = db.select(
                self.Items.c.id,
                self.Items.c.title,
                self.Items.c.description,
                self.ItemCategory.c.categoryId.label("category_id")).where(
                    (self.Items.c.id == item_id) & 
                    (self.ItemCategory.c.itemId == item_id))
            results = self.session.execute(stmt).mappings().all()
            return results 

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def count_items(self, filter_str="{}"):
        filter_dict = json.loads(filter_str)
        stmt = db.select(db.func.count()).select_from(self.Items)
        for key, value in filter_dict.items():
            if hasattr(self.Items.c, key):
                stmt = stmt.where(getattr(self.Items.c, key) == value)
        return self.session.execute(stmt).scalar()


        
    


        
    

        


