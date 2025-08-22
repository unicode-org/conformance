// Tests date/time formatting

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat

const debug = 0;

// Converting skeleton to options
const skeleton_to_options_map = new Map(
    [
      ['G', {era: 'short'} ],
      ['GG', {era: 'short'} ],
      ['GGG', {era: 'short'} ],
      ['GGGG', {era: 'long'} ],
      ['GGGGG', {era: 'narrow'} ],

      ['y', {'year': 'numeric'} ],
      ['yy', {'year': '2-digit'} ],
      ['yyy', {'year': 'numeric'} ],
      ['yyyy', {'year': 'numeric'} ],

      // Quarter not supported

      ['M', {'month': 'numeric'} ],
      ['MM', {'month': '2-digit'} ],
      ['MMM', {'month': 'short'} ],
      ['MMMM', {'month': 'long'} ],
      ['MMMMM', {'month': 'narrow'} ],

      ['L', {'month': 'numeric'} ],
      ['LL', {'month': '2-digit'} ],
      ['LLL', {'month': 'short'} ],
      ['LLLL', {'month': 'long'} ],
      ['LLLLL', {'month': 'narrow'} ],

      // Week not supported

      ['d', {'day': 'numeric'} ],
      ['dd', {'day': '2-digit'} ],

      ['E', {'weekday': 'short'} ],
      ['EE', {'weekday': 'short'} ],
      ['EEE', {'weekday': 'short'} ],
      ['EEEE', {'weekday': 'long'} ],
      ['EEEEE', {'weekday': 'narrow'} ],

      ['h', {'hourCycle': 'h12', 'hour': 'numeric'} ],
      ['hh', {'hourCycle': 'h12', 'hour': '2-digit'} ],
      ['H', {'hourCycle': 'h24', 'hour': 'numeric'} ],
      ['HH', {'hourCycle': 'h24', 'hour': '2-digit'} ],

      ['j', {'hour': 'numeric'} ],
      ['jj', {'hour': '2-digit'} ],

      ['m', {'minute': 'numeric'} ],
      ['mm', {'minute': '2-digit'} ],

      ['s', {'second': 'numeric'} ],
      ['ss', {'second': '2-digit'} ],

      ['z', {'timeZoneName': 'short'} ],
      ['zzzz', {'timeZoneName': 'long'} ],

      ['O', {'timeZoneName': 'shortOffset'} ],
      ['OOOO', {'timeZoneName': 'longOffset'} ],

      ['v', {'timeZoneName': 'shortGeneric'} ],
      ['vvvv', {'timeZoneName': 'longGeneric'} ],

      ['V', {'timeZoneName': 'shortGeneric'} ],
      ['VV', {'timeZoneName': 'shortGeneric'} ],
      ['VVV', {'timeZoneName': 'shortGeneric'} ],
      ['VVVV', {'timeZoneName': 'longGeneric'} ],
    ]
);

// E.g., "yyDEEEE" --> ["yy", "D", "EEEE"]
function split_skeleton_into_fields(skeleton) {
  return skeleton.match(/(.)\1*/g) || [];
}

function fill_options_from_skeleton_parts(skeleton_parts) {
  let skeleton_options = {};
  if (skeleton_parts === undefined || skeleton_parts == null) {
    return skeleton_options;
  }
  for (const part of skeleton_parts) {
    if (skeleton_to_options_map.has(part)) {
      let options = skeleton_to_options_map.get(part);
      Object.assign(skeleton_options, options);
    } else {
      console.log(
          '# NodeJS: DateTimeFormat: UNKNOWN MAPPING FOR PART = %s',
          part);
    }
  }
  return skeleton_options;
}


module.exports = {
  testDateTimeFmt: function (json) {
    const label = json['label'];
    let locale = json['locale'];
    const intl_locale = new Intl.Locale(locale);
    if (! locale) {
      locale = 'und';
    }

    let input_options = {};
    let test_options = {};

    if (json['options']) {
      input_options = json['options'];
    }

    // Handle skeleton specification.
    if (input_options && 'skeleton' in input_options) {
      let skeleton = input_options['skeleton'];
      let split = split_skeleton_into_fields(skeleton);
      if (debug > 0) {
        console.log('# skeleton: %s, options %s', skeleton, split);
      }

      test_options = fill_options_from_skeleton_parts(split);
      if (debug > 0) {
        console.log('# TEST_OPTIONS: %s', split, test_options);
      }
    }

    let return_json = {'label': label};

    let timezone;
    if ('timeZone' in input_options) {
      test_options['timeZone'] = input_options['timeZone'];
    }

    if ('zoneStyle' in input_options) {
      test_options['zoneStyle'] = input_options['zoneStyle'];
    }

    // Get the date from input milliseconds.
    // Prefer milliseconds
    let iso_date;
    let test_date;

    // Parse the input string as a date.
    if (json['input_string']) {
      iso_date = json['input_string'];
      // Remove anything starting with "["
      let option_start = iso_date.indexOf('[');
      let test_date_string;
      if (option_start >= 0) {
        // TODO: !! Get the timezone and calendar from the iso_date string.
        test_date_string = iso_date.substring(0, option_start);
      } else {
        test_date_string = iso_date;
      }
      test_date = new Date(test_date_string);
    }

    // Get date and time styles
    let dateStyle;
    let timeStyle;

    if ('timeStyle' in input_options) {
      test_options['timeStyle'] = input_options['timeStyle'];
    }
    if ('dateStyle' in input_options) {
      test_options['dateStyle'] = input_options['dateStyle'];
    }

    if ('dateTimeFormatType' in input_options &&
        input_options['dateTimeFormatType'] == 'standard') {
      return_json['error_type'] = 'unsupported';
      return_json['error_detail'] = input_options['dateTimeFormatType'];
        return_json['unsupported'] = 'format type';
        return return_json;
    }

    if ('semanticSkeleton' in input_options) {
      // Check for known issue when format output should give only the time zone.
      if (input_options['semanticSkeleton'] == 'Z') {
        return_json['error'] = 'unsupported';
        return_json['error_detail'] = 'Requested timezone without date or time';
        return_json['unsupported'] = 'timezone only';
        return return_json;
      }
    }

    let calendar;
    try {
      calendar = input_options['calendar'];
      test_options['calendar'] = calendar;
    } catch {
      calendar = null;
    }
    try {
      if (calendar) {
        const supported_calendars = intl_locale.calendars;
        // Check if the calendar system is supported in this locale.
        // If not, skip the test.
        if ( !supported_calendars.includes(calendar)) {
          return_json['unsupported'] = ': ' + error.message;
          return return_json;
        }
      }
    } catch(error) {
      // This is not yet supported.
    }

    let dt_formatter;
    try {
      dt_formatter = new Intl.DateTimeFormat(locale, test_options);
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'DateTimeFormat Constructor: ' + error.message;
      return return_json;
    }

    try {
      const formatted_dt = dt_formatter.format(test_date);
      return_json['actual_options'] = test_options;
      return_json['result'] = formatted_dt;
    } catch (error) {
      return_json['unsupported'] = ': ' + error.message;
    }
    return return_json;
  }
}
