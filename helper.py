#Module containing the logic functions

def removeEmptyLines(text):
    lines = text.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]

    string_without_empty_lines = ""
    for line in non_empty_lines:
        string_without_empty_lines += line + "\n"

    return(string_without_empty_lines)


def sortTimings(new_timings_array):
    # Sort timings and return (None if input wrong format)
    # Go through new timings and return array of timings in a nested array
    sorted_timings = []
    
    try:
        for new_timings in new_timings_array:
            
            tidiedText = removeEmptyLines(new_timings)

            for line in tidiedText.splitlines():
                stripped_line = line.strip()
                timeStr = stripped_line[0:4]

                # Append tuple of timing(int) and the associated line
                sorted_timings.append((int(timeStr), stripped_line))

        # Sort by timing(int)
        takeFirst = lambda tuple:tuple[0] 
        sorted_timings.sort(key=takeFirst)

        final_string = ""
        for timing_tuple in sorted_timings:
            final_string += (timing_tuple[1]+"\n")

        return final_string

    except:
        return None

def break_long_texts(text):
    lines = text.split("\n")
    
    i = 1
    split_text_array = []
    text_substring = ""

    if(len(lines) > 70):
        for line in lines:
            # Add lines into chunks of 70 lines max
            if(i <= 70):
                text_substring += f"\n"+line 
                i += 1
            else:
                split_text_array.append(text_substring)
                text_substring = f"\n"+line
                i = 1
        return split_text_array
    
    else:
        return [text]
    
    