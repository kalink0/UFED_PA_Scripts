# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# AUTHOR:         kalink0
# MAIL:           kalinko@be-binary.de
# CREATION DATE:  2019/08/30
#
# LICENSE:        CC0-1.0
#
# SOURCE:         https://github.com/kalink0/UFED_PA_Scripts\Android
#
# TITLE:          facebook_messenger_light_parser
#
# DESCRIPTION:   Parser for Android App Facebook Messenger Light (com.facebook.mlite)
#				 Version 60.0.1.14.238. 
#				 Written for UFED PA 7.22
#                The Script extracts Contacts and Messages from the core.db
#				 and maps it to the corresponding models in UFED PA.
#
# KNOWN RESTRICTIONS:
#                
#                
#
# USAGE EXAMPLE:  Execute Script in UFED PA
#
# -------------------------------------------------------------------------------

from physical import *
import SQLiteParser
from System.Convert import IsDBNull

class FacebookMessengerLightParser(object):
    '''
    Facebook Messenger Light Parser, version 60.0.1.14.238
    Parses contacts and chats.
    '''
    def __init__(self, node):
        self.node = node
        self.APP_NAME = 'Facebook Messenger Light'
        self.node = node

        self.db = None
		
		
        self.user_account = UserAccount()
		self.user_account.ServiceType.Value = self.APP_NAME
        self.contacts={}
		self.messages={}

    def parse(self):
        self.db = SQLiteParser.Database.FromNode(self.node)
		if self.db is None:
            return
		
        results = []
        self.decode_account()
        results = self.user_account       
        #results+=self.contacts.values()
        
        return results
	
	def decode_account(self):
		'''
		Parses Account data - currently from db in the app directory.
		Will be changed to account xml asap if possible. It is just the first test for this script
		'''
		# Get content of the table shared_queues
		for line in self.db['shared_queues']:
			pass
		
		# Set values of UserID entity
		uid = UserID()
		uid.Deleted = DeletedState.Intact
		# Set Facebook ID for UserID
		uid.Category.Value = "Facebook ID"
		uid.Value.Value = line['collection_topic'].Value
		
		self.user_account.Entries.Add(uid)
		
	
	def decode_chats(self):
		pass

    def decode_contacts(self):
        '''
        parses contacts
        '''
        
		



# Getting the node from the filesystem
# TODO: make the filesystems dynamically usable (search over all available FSs for the db)
node = ds.FileSystems[5]['/Root/data/com.facebook.mlite/databases/omnistore.db']

#calling the parser for results
results = FacebookMessengerLightParser(node).parse()

#adding the results to the tree view
ds.Models.Add(results)
