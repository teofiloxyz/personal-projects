#!/usr/bin/python3

class Questions:
    @staticmethod
    def opts(question: str, opts_dict: dict, invalid_msg=None):
        while True:
            ans = input(question)
            if ans == 'q':
                return ans
            elif ans in opts_dict.keys():
                return opts_dict[ans]
            if invalid_msg is None:
                opts = ','.join(key for key in opts_dict.keys())
                print('Invalid answer\nPlease choose one of the following: '
                      f'{opts}')
            else:
                print(invalid_msg)

    @staticmethod
    def get_date(question: str, date_type="%Y-%m-%d",
                 answer=None, use_rofi=False):
        from datetime import datetime
        from Tfuncs import rofi

        message = ""
        while True:
            if answer is None:
                if use_rofi:
                    date = rofi.simple_prompt(question, message)
                else:
                    date = input(question)
            else:
                date = answer

            if date == 'q':
                return date

            current_year = datetime.now().strftime('%Y')
            if date == '':
                date = datetime.now().strftime('%d-%m-%Y')
            elif date.count('-') == 0:
                current_month = datetime.now().strftime('%m')
                date = date + '-' + current_month + '-' + current_year
            elif date.count('-') == 1:
                date = date + '-' + current_year

            date_d, date_m, date_y = date.split('-')
            if len(date_m) == 1:
                date_m = '0' + date_m
            if len(date_y) == 2:
                date_y = '20' + date_y
            date = date_d + '/' + date_m + '/' + date_y
            try:
                date = datetime.strptime(date, "%d/%m/%Y")
                return date.strftime(date_type)
            except ValueError:
                message = "Invalid date"
                print(message)
                if answer is not None:
                    return 'q'

    @staticmethod
    def get_hour(question: str, hour_type="%H:%M:%S",
                 answer=None, use_rofi=False):
        from datetime import datetime
        from Tfuncs import rofi

        message = ""
        while True:
            if answer is None:
                if use_rofi:
                    hour = rofi.simple_prompt(question, message)
                else:
                    hour = input(question)
            else:
                hour = answer

            if hour == 'q':
                return hour
            elif hour == '':
                hour = '09-00'
            elif hour.count('-') == 0:
                hour = hour + '-' + '00'
            hour = hour.replace('-', ':')
            try:
                hour = datetime.strptime(hour, hour_type)
            except ValueError:
                message = "Invalid hour"
                print(message)
                if answer is not None:
                    return 'q'
                continue
            break
        return hour.strftime(hour_type)


class Inputs:
    @staticmethod
    def files(question: str, extensions, file_input=None,
              multiple=False):
        import os

        def get_path(question):
            file_input = input(question)
            if file_input == '':
                return False
            return file_input

        def check_path(file_input, extensions):
            if not os.path.exists(file_input):
                print('Invalid answer, file does not exist')
                return False
            if file_input.split('.')[-1] not in extensions:
                print('Invalid answer, file format is not valid for input')
                return False

        if type(extensions) == str:
            extensions = (extensions)

        if file_input is not None:
            if check_path(file_input, extensions) is False:
                return False
            return True

        if multiple:
            files_list = []
            while True:
                file_input = get_path(question)
                if file_input == 'q':
                    return file_input
                elif file_input is False:
                    break
                elif check_path(file_input, extensions) is False:
                    continue
                files_list.append(file_input)
            return files_list
        else:
            while True:
                file_input = get_path(question)
                if file_input == 'q':
                    return file_input
                elif file_input is False:
                    print("If you want to abort enter 'q'")
                    continue
                elif check_path(file_input, extensions) is False:
                    continue
                return file_input

    @staticmethod
    def dirs(question: str, dir_input=None, multiple=False, use_rofi=False):
        import os
        from Tfuncs import rofi

        def get_path(question, message):
            if use_rofi:
                dir_input = rofi.simple_prompt(question, message)
            else:
                dir_input = input(question)
            if dir_input == '':
                return False
            return dir_input

        def check_path(dir_input):
            if not os.path.exists(dir_input):
                message = 'Invalid answer, directory does not exist'
                print(message)
                return False, message
            return True, ""

        if dir_input is not None:
            if check_path(dir_input) is False:
                return False
            return True

        message = ""
        if multiple:
            dirs_list = []
            while True:
                dir_input = get_path(question, message)
                if dir_input == 'q':
                    return dir_input
                elif dir_input is False:
                    break
                good_path, message = check_path(dir_input)
                if not good_path:
                    continue
                dirs_list.append(dir_input)
            return dirs_list
        else:
            while True:
                dir_input = get_path(question, message)
                if dir_input == 'q':
                    return dir_input
                elif dir_input is False:
                    message = "If you want to quit enter 'q'"
                    print(message)
                    continue
                good_path, message = check_path(dir_input)
                if not good_path:
                    continue
                return dir_input


class Outputs:
    @staticmethod
    def files(question: str, extension=None, file_input=None, file_output=None,
              output_name=None, output_name_change=False):
        import os

        def check_path(file_output):
            file_output_dir = os.path.dirname(file_output)
            if not os.path.exists(file_output_dir):
                print('Invalid answer, directory for output does not exist')
                return False
            if os.path.exists(file_output) and output_name_change is False:
                print('Invalid answer, name of output already exists')
                return False

        if file_output is not None:
            if check_path(file_output) is False:
                return False
            return True

        if extension is not None:
            if extension[0] == '.':
                extension = extension[1:]

        while True:
            file_output = input(question)
            if file_output == 'q':
                return file_output
            elif '/' in file_output:
                if os.path.isdir(file_output):
                    if output_name is not None:
                        file_output = os.path.join(file_output, output_name)
                    elif file_input is not None:
                        input_name = os.path.basename(file_input)
                        file_output = os.path.join(file_output, input_name)
                if extension is not None:
                    if not file_output.endswith(extension):
                        file_output = file_output + '.' + extension
            elif file_input is not None:
                file_input_dir = os.path.dirname(file_input)
                if file_output == '':
                    file_input_dir_no_ext = os.path.splitext(file_input)[0]
                    if extension is not None:
                        file_output = file_input_dir_no_ext \
                            + '_output.' + extension
                    else:
                        file_output = file_input
                else:
                    if extension is not None:
                        if not file_output.endswith(extension):
                            file_output = os.path.join(file_input_dir,
                                                       file_output
                                                       + '.' + extension)
                        else:
                            file_output = os.path.join(file_input_dir,
                                                       file_output)
                    else:
                        input_extension = os.path.splitext(file_input)[-1]
                        file_output = os.path.join(file_input_dir,
                                                   file_output
                                                   + input_extension)
            else:
                print('Invalid answer, give a complete path please')
                continue

            if extension is None:
                file_output_basename = os.path.basename(file_output)
                if '.' in file_output_basename[1:]:
                    if file_output_basename[0] == '.':
                        file_output_name = '.' \
                            + file_output_basename.split('.')[1]
                    else:
                        file_output_name = file_output_basename.split('.')[0]
                    if file_input is None:
                        file_output = os.path.join(os.path.
                                                   dirname(file_output),
                                                   file_output_name)
                    else:
                        input_extension = os.path.splitext(file_input)[-1]
                        file_output = os.path.join(os.path.
                                                   dirname(file_output),
                                                   file_output_name
                                                   + input_extension)

            if check_path(file_output) is False:
                continue
            return file_output

    @staticmethod
    def dirs(question: str, dir_output=None):
        import os

        def check_path(dir_output):
            if not os.path.exists(dir_output):
                os.makedirs(dir_output, exist_ok=True)

        if dir_output is not None:
            check_path(dir_output)
            return True

        while True:
            dir_output = input(question)
            if dir_output in ('', 'q'):
                return dir_output
            check_path(dir_output)
            return dir_output
