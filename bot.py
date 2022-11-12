from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram import Update
from telegram.ext import (Updater,
                          CommandHandler,
                          CallbackQueryHandler,
                          CallbackContext,
                          ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Custom modules
from helper import sortTimings, break_long_texts

BOT_TOKEN = <BOT_TOKEN>

# Assign an int value for each state
EXPECT_SITREP, EXPECT_BUTTON_CLICK,  = range(2)

START_MESSAGE = '''
Hello 77 Batch🤖.
Below are the list of commands to use the bot
    
**COMMANDS**
1.Sort SITREP timings 
  (Takes multiple sitreps)
  /sort_timeline
    
DRIVE YOUR FEET TO THE GROUND'''

def start(update: Update, context: CallbackContext):
    
    update.message.reply_text(START_MESSAGE)


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
    ''' The user's reply to the name prompt comes here  '''
    sitrep_chunk = update.message.text

    # Save text chunk in context
    context.user_data['sitrep_data'] += [sitrep_chunk]

    # Provide Button to add more sitrep chunks
    more_button = InlineKeyboardButton("Add More", callback_data='more')
    done_button = InlineKeyboardButton("Done ✅", callback_data='done')
    markup = InlineKeyboardMarkup([[more_button], [done_button]])
    update.message.reply_text(f'Chunk Included.', reply_markup=markup)

    # ends this particular conversation flow
    return EXPECT_BUTTON_CLICK


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Name Conversation cancelled by user. Bye. Send /set_name to start again')
    return ConversationHandler.END


if __name__ == "__main__":

    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    _handlers = {}

    _handlers['start_handler'] = CommandHandler('start', start)

    _handlers['timeline_convo_handler'] = ConversationHandler(
        entry_points=[CommandHandler('sort_timeline', sort_timeline_handler)],
        states={
            EXPECT_SITREP: [MessageHandler(Filters.text, sitrep_input)],
            EXPECT_BUTTON_CLICK: [CallbackQueryHandler(button_click_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    for name, _handler in _handlers.items():
        dispatcher.add_handler(_handler)

    updater.start_polling()
    updater.idle()