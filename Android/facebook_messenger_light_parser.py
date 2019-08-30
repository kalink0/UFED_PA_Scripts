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
        self.core_db_node = node + '/databases/core.db'
		self.omnistore_db_node = node + '/databases/omnistore.db'
		
        self.core_db = None
		self.omnistore_db = None
		
        self.user_account = UserAccount()
		self.user_account.ServiceType = self.APP_NAME
        self.contacts={}
		self.messages={}

    def parse(self):
        self.core_db = SQLiteParser.Database.FromNode(self.core_db_node)
		if self.core_db is None:
            return
        
		self.omnistore_db = SQLiteParser.Database.FromNode(self.omnistore_db_node)
		if self.omnistore_db is None:
            return
		
        results = []
        self.decode_account()
        results += self.user_account       
        #results+=self.contacts.values()
        return results
	
	def decode_account(self):
		'''
		Parses 
		'''
		db = SQLiteParser.Database.FromNode(self.omnistore_db_node)
		# Get content of the table shared_queues
		for line in db['shared_queues']:
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
        
		
        #user account - we are taking the name of the node and getting the number,
        #in BeeTalk the user accounts are ending with '00', so we add it.
        pos=self.node.AbsolutePath.rfind('/')
        ua_id = self.node.AbsolutePath[pos+6:pos+14] + '00'

        #creating new UserID
        uid = UserID()

        #setting the Deleted State of the UserID
        uid.Deleted = DeletedState.Intact
        #Setting values
        uid.Category.Value = self.APP_NAME+ " Id"
        uid.Value.Value = ua_id

        #creating new UserAccount
        ua = UserAccount()

        #setting the Deleted State and other Properties of the UserAccount 
        ua.Deleted = DeletedState.Intact
        ua.ServiceType.Value = self.APP_NAME
        ua.Entries.Add(uid)
        self.contacts[ua_id] = ua
        self.user_account = ua
        
        #going over the contacts table 
        if 'bb_buddy_id_info' not in self.db.Tables:
            return

        #Setting the signatures of the table
        ts = SQLiteParser.TableSignature('bb_buddy_id_info')
        
        #`userid` is Int
        SQLiteParser.Tools.AddSignatureToTable(ts, '`userid`', SQLiteParser.FieldType.Int)
        #`id` is Int
        SQLiteParser.Tools.AddSignatureToTable(ts, '`id`', SQLiteParser.FieldType.Int)
        #`categoryid` is byte or 0
        SQLiteParser.Tools.AddSignatureToTable(ts, '`categoryid`', SQLiteParser.Tools.SignatureType.Byte, SQLiteParser.Tools.SignatureType.Const0)
        #`option` is byte or 0
        SQLiteParser.Tools.AddSignatureToTable(ts, '`option`', SQLiteParser.Tools.SignatureType.Byte, SQLiteParser.Tools.SignatureType.Const0)

        #going over the records of bb_buddy_id_info table
        for rec in self.db.ReadTableRecords(ts, True):
            #checking the validity of the record
            if IsDBNull(rec['`userid`'].Value) or rec['`userid`'].Value == 0:
                continue

            #creating new UserID field
            uid = UserID()
            uid.Deleted = rec.Deleted
            uid.Category.Value = self.APP_NAME+ " Id"
            uid.Value.Value = str(rec['`userid`'].Value) + '00'
            uid.Value.Source = MemoryRange(rec['`userid`'].Source)
            user = Contact()
            user.Deleted = rec.Deleted
            user.Source.Value = self.APP_NAME
            user.Entries.Add(uid)
            self.contacts[uid.Value.Value] =user

        # avatar and user id
        if 'bb_user_info' in self.db.Tables:
            ts = SQLiteParser.TableSignature('bb_user_info')
            
            SQLiteParser.Tools.AddSignatureToTable(ts, '`userid`', SQLiteParser.FieldType.Int)
            SQLiteParser.Tools.AddSignatureToTable(ts, '`aliasInfo_id`',SQLiteParser.Tools.SignatureType.Const0,SQLiteParser.Tools.SignatureType.Null)
            SQLiteParser.Tools.AddSignatureToTable(ts, '`name`',SQLiteParser.Tools.SignatureType.Text)
            SQLiteParser.Tools.AddSignatureToTable(ts, '`gender`',SQLiteParser.Tools.SignatureType.Const0,SQLiteParser.Tools.SignatureType.Const1)
                
            for rec in self.db.ReadTableRecords(ts, True):
                if IsDBNull(rec['`customized_id`'].Value):
                    continue
                customized_id = rec['`customized_id`'].Value
                for u in self.contacts.values():
                    uid = u.Entries[0].Value.Value
                    if uid == customized_id:
                        SQLiteParser.Tools.ReadColumnToField(rec, '`name`', u.Name, True)
                        if not IsDBNull(rec['`avatar`'].Value) and not rec['`avatar`'].Value == 1:
                            self.add_avatar_to_user(u,rec)

    def add_avatar_to_user(self,user,rec):
        avatar=str(rec['`avatar`'].Value)
        pics_sizes=[]
        pics_sizes.append(avatar+"-large")
        pics_sizes.append(avatar+"-large-r")
        pics_sizes.append(avatar+"-large-rnd")
        pics_sizes.append(avatar+"-med")
        pics_sizes.append(avatar+"-med-r")
        pics_sizes.append(avatar+"-med-rnd")
        pics_sizes.append(avatar)
        pics_sizes.append(avatar+"-r")
        pics_sizes.append(avatar+"-rnd")

        cp = ContactPhoto()
        cp.Deleted = rec.Deleted
        self.node.Parent
        
        root = self.node.Parent.Parent.Parent.Parent.GetByPath('shared')
        if root is None or len(root.Children) == 0:
            root = self.node.Parent.Parent.Parent.Parent.GetByPath('media')
                
        if root is not None:
            pic_nodes = root.Search('/beetalk/avatar/'+avatar)
            
            found_largest_pic = False
            for pic_size in pics_sizes:
                if not found_largest_pic:
                    for f_pic in pic_nodes:
                        if f_pic.Name == pic_size:
                            cp.Name.Value = f_pic.Name
                            cp.PhotoNode.Value = f_pic
                            found_largest_pic = True
                            break
        if cp.PhotoNode.HasContent:                
            user.Photos.Add(cp)


# Getting the node from the filesystem
# TODO: make the filesystems dynamically usable (search over all available FSs for the db)
node = ds.FileSystems[5]['/Root/data/com.facebook.mlite']

#calling the parser for results
results = FacebookMessengerLightParser(node).parse()

#adding the results to the tree view
ds.Models.AddRange(results)
