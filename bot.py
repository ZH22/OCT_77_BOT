from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram import Update
from telegram.ext import (Updater,
                          CommandHandler,
                          CallbackQueryHandler,
                          CallbackContext,
                          ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

# Custom modules
from helper import sortTimings, break_long_texts

BOT_TOKEN = <BOT_TOKEN>
EXPECT_SITREP, EXPECT_BUTTON_CLICK, EXPECT_GROUP, EXPECT_TRAVEL, EXPECT_WHO, EXPECT_LOCATION, EXPECT_FIRST_LOC, EXPECT_SEC_LOC, EXPECT_TIMING, EXPECT_COMPLETED = range(10)

START_MESSAGE = '''
Hello 77 Batch🤖.
[Temporary scuffed bot with only relevant features (Will Upgrade in the Future)]
Below are the list of commands to use the bot
    
**COMMANDS**
1.Sort SITREP timings 
  (Takes multiple sitreps)
  /sort_timeline

2. Generate SITREP
   (Forming up and Reaching places)
   /generate_sitrep

DRIVE YOUR FEET TO THE GROUND'''

def start(update: Update, context: CallbackContext):
    
    update.message.reply_text(START_MESSAGE)

# SORT TIMELINE FEATURE=======================================================================
def sort_timeline_handler(update: Update, context: CallbackContext):
    # Reset sitrep_data array
    context.user_data['sitrep_data'] = []
    update.message.reply_text('Send the first SITREP timeline text')
    return EXPECT_SITREP


def button_click_handler(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.data == 'more':
        query.edit_message_text(f'Send another SITREP Chunk')
        return EXPECT_SITREP
    
    elif query.data == 'done':
        
        timingsArray = context.user_data['sitrep_data']
        sortedTimings = sortTimings(timingsArray)
        
        if sortedTimings is not None:
            query.edit_message_text("👇Sorted the SITREP👇")
            # Break up the potentially long text into chunks of max 70 lines and send
            sorted_timings_array = break_long_texts(sortedTimings)
            
            for text in sorted_timings_array:
                context.bot.send_message(update.effective_chat.id, text)
            
            # Remind User there might be more than one message sent  
            context.bot.send_message(update.effective_chat.id, f"☝️Generated {len(sorted_timings_array)} message(s)☝️")
        else:
            query.edit_message_text("There's probably something wrong with the input format\nCheck and try again")

        return ConversationHandler.END


def sitrep_input(update: Update, context: CallbackContext):
    sitrep_chunk = update.message.text

    # Save text chunk in context
    context.user_data['sitrep_data'] += [sitrep_chunk]

    # Provide Button to add more sitrep chunks
    more_button = InlineKeyboardButton("Add More", callback_data='more')
    done_button = InlineKeyboardButton("Done ✅", callback_data='done')
    markup = InlineKeyboardMarkup([[more_button], [done_button]])
    update.message.reply_text(f'Chunk Included.', reply_markup=markup)
    return EXPECT_BUTTON_CLICK

# =================================================================================================
# GENERATE SITREP FEATURE
def generate_sitrep_handler(update: Update, context: CallbackContext):
    squad_button = InlineKeyboardButton("SQUAD", callback_data='squad')
    subgroup_button = InlineKeyboardButton("SUBGROUP", callback_data='subgroup')
    markup = InlineKeyboardMarkup([[squad_button, subgroup_button]])
    update.message.reply_text("SITREP\nWhat's your group type?", reply_markup=markup)
    
    # Reset merged_sitreps to emtpy string
    context.user_data['merged_sitrep'] = ""
    # return EXPECT_GROUP
    return EXPECT_GROUP

TRAVEL_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("Formed Up", callback_data='formed up'), InlineKeyboardButton("Reached", callback_data='reached')], 
])

def group_click_handler(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.data == 'squad':
        context.user_data['isSubgroup'] = False
        query.edit_message_text("Type of Travel?", reply_markup=TRAVEL_MARKUP)

        return EXPECT_TRAVEL

    elif query.data == 'subgroup':
        context.user_data['isSubgroup'] = True
        # if group is subgroup (ask who is inside)
        query.edit_message_text(f'Who is in the group?\n(e.g. OCT Ace, OCT Bob and OCT Cat)')
        return EXPECT_WHO

def subgroup_who_handler(update: Update, context: CallbackContext):
    context.user_data['subgroup_names'] = update.message.text
    context.bot.send_message(update.effective_chat.id,"Type of Travel?", reply_markup=TRAVEL_MARKUP)

    return EXPECT_TRAVEL

LOCATIION_MARKUP =  InlineKeyboardMarkup([
    [InlineKeyboardButton("Coyline", callback_data='Coyline'), InlineKeyboardButton("Mess", callback_data='Mess')],
    [InlineKeyboardButton("Stadium", callback_data='Stadium'), InlineKeyboardButton("Drill Shed", callback_data='Drill Shed')],
    [InlineKeyboardButton("OB", callback_data='OB'), InlineKeyboardButton("Tennis", callback_data='Tennis Court')],
    [InlineKeyboardButton("Blk 12", callback_data='Blk 12'), InlineKeyboardButton("Zebra-X", callback_data='Zebra Crossing')],
    [InlineKeyboardButton("Dojo", callback_data='Dojo'), InlineKeyboardButton("Unity Sq", callback_data='Unity Square')],
    [InlineKeyboardButton("CUSTOM(manual edit)", callback_data='*CUSTOM*')]
])

def travel_click_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['temp_travel'] = query.data

    if query.data == 'formed up':
        query.edit_message_text("🚀 Start Location 🚀?", reply_markup=LOCATIION_MARKUP)
        return EXPECT_FIRST_LOC
    
    elif query.data == 'reached':
        query.edit_message_text("Location?", reply_markup=LOCATIION_MARKUP)
        return EXPECT_LOCATION

    
def first_loc_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['start_loc'] = query.data
    
    query.edit_message_text("🚧 End Location? 🚧", reply_markup=LOCATIION_MARKUP)
    return EXPECT_SEC_LOC

def sec_loc_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['end_loc'] = query.data
    
    query.edit_message_text("Timing?🕒\nType Below")
    return EXPECT_TIMING

def loc_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['location'] = query.data
    
    query.edit_message_text("Timing?🕒\nType Below")
    return EXPECT_TIMING

def timing_handler(update: Update, context: CallbackContext):
    answer = update.message.text

    # Keep asking until time is valid
    try:
        if int(answer) >= 0000 and int(answer) < 2400 and int(answer[2:4]) < 60:
            context.user_data['temp_timing'] = answer
            # (ADD LATER COMPILE AND STORE VALUES)
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("Add more", callback_data='more'), InlineKeyboardButton("Done ✅", callback_data='done')]])
            context.bot.send_message(update.effective_chat.id, "Completed?", reply_markup=markup)
            return EXPECT_COMPLETED

        else:
            context.bot.send_message(update.effective_chat.id,"Invalid TIMING. Please send again")
            return EXPECT_TIMING
    except:
        context.bot.send_message(update.effective_chat.id,"Invalid TIMING. Please send again")
        return EXPECT_TIMING

def new_sitrep_line(context: CallbackContext):
    # Create formatted string of sitrep timing
    data = context.user_data
    formed_string = f"{data['temp_timing']} - " 

    if data['isSubgroup']:
        # IF subgroup send text with names in front
        formed_string += f"{data['subgroup_names']} "
    
    if data['temp_travel'] == 'formed up':
        formed_string += f"Formed up at {data['start_loc']} to move to {data['end_loc']}"
    
    elif data['temp_travel'] == 'reached':
        formed_string += f"Reached {data['location']}"
    
    return formed_string 

def sitrep_completed_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['merged_sitrep'] += f"{new_sitrep_line(context)}\n"

    if query.data == 'more':
        query.edit_message_text("Next SITREP Movement", reply_markup=TRAVEL_MARKUP)
        return EXPECT_TRAVEL
    
    elif query.data == 'done':
        merged_sitrep = context.user_data['merged_sitrep']
        merged_sitrep = sortTimings([merged_sitrep])

        query.edit_message_text(merged_sitrep)
        return ConversationHandler.END
# =================================================================================================

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Cancelled by user. Bye. Send the command to start again')
    return ConversationHandler.END


if __name__ == "__main__":

    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    # command handlers ==============================================================
    _handlers = {}

    # START COMMAND
    _handlers['start_handler'] = CommandHandler('start', start)

    # SORT_TIMELINE COMMAND
    _handlers['timeline_convo_handler'] = ConversationHandler(
        entry_points=[CommandHandler('sort_timeline', sort_timeline_handler)],
        states={
            EXPECT_SITREP: [MessageHandler(Filters.text, sitrep_input)],
            EXPECT_BUTTON_CLICK: [CallbackQueryHandler(button_click_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # GENERATE_SITREP COMMAND
    _handlers['sitrep_convo_handler'] = ConversationHandler(
        entry_points=[CommandHandler('generate_sitrep', generate_sitrep_handler)],
        states={
            EXPECT_GROUP: [CallbackQueryHandler(group_click_handler)],
            EXPECT_WHO: [MessageHandler(Filters.text, subgroup_who_handler)],
            EXPECT_TRAVEL: [CallbackQueryHandler(travel_click_handler)],
            EXPECT_FIRST_LOC: [CallbackQueryHandler(first_loc_handler)],
            EXPECT_SEC_LOC: [CallbackQueryHandler(sec_loc_handler)],
            EXPECT_LOCATION: [CallbackQueryHandler(loc_handler)],
            EXPECT_TIMING: [MessageHandler(Filters.text, timing_handler)],
            EXPECT_COMPLETED: [CallbackQueryHandler(sitrep_completed_handler)]
            
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # ===============================================================================

    # dispatching commands 
    for name, _handler in _handlers.items():
        dispatcher.add_handler(_handler)

    updater.start_polling()
    updater.idle()