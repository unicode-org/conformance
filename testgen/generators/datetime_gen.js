/* Generate date/time test data with the following dimensions:

   1. locale
   2. calendar (e.g., gregorian, hebrew, roc, islamic...
   3. spec:
   a. date style
   b. time style
   c. both date style and time
   d. patterns (e.g., "G y")
   4. date values (milliseconds, year, etc.
*/

// Set up Node version to generate data specific to ICU/CLDR version
// e.g., `nvm install 21.6.0;nvm use 21.6.0` (ICU 74)

const gen_hash = require("./generate_test_hash.js");

require("temporal-polyfill/global");

const fs = require('node:fs');

const debug = false;

const skip_things = false;  // To limit some options for generating tests

// Controls if milliseconds value is stored in test cases in addition to ISO string.
let use_milliseconds = false;

// Add numbering system to the test options
// Don't test these across all other options, however.
const numbering_systems = ['latn', 'arab', 'beng']

// ICU4X locales, maybe 20
// Don't include "und" as a locale because the behavior depends on the platform.
const locales = [
  'en-US', 'en-GB',
  'zh-TW', 'vi', 'ar', 'mt-MT',
  'bn', 'zu'
];

      // maybe 10 calendars
const calendars = ['gregory',
                   'buddhist', 'hebrew', 'chinese', 'roc', 'japanese',
                   'islamic', 'islamic-umalqura', 'persian'
                  ];

// (numsysm, skeleton, timezone) ~`00
const spec_options = [
  // Removed empty option list
  {'dateStyle': 'short', 'timeStyle': 'short'},
  {'dateStyle': 'medium', 'timeStyle': 'medium'},
  {'dateStyle': 'long', 'timeStyle': 'long'},
  {'dateStyle': 'full', 'timeStyle': 'full'},
  {'dateStyle': 'full', 'timeStyle': 'short'},
  {'dateStyle': 'long'},
  {'timeStyle': 'long'},
  {'hour': 'numeric'},
  // {'hour': '2-digit'},  // ?? remove this ?
  {'hour': 'numeric', 'minute': 'numeric'},
  {'hour': 'numeric', 'minute': 'numeric', 'second': "numeric"},
  {'hour': 'numeric', 'minute': 'numeric', 'second': "numeric", 'fractionalSecondDigits': 1},
  {'hour': 'numeric', 'minute': 'numeric', 'second': "numeric", 'fractionalSecondDigits': 2},
  {'hour': 'numeric', 'minute': 'numeric', 'second': "numeric", 'fractionalSecondDigits': 3},
  {'hour': 'numeric', 'minute': 'numeric', 'second': "numeric"},
  {'hour': 'numeric', 'minute': 'numeric'},
  // {'hour': '2-digit', 'minute': 'numeric'},
  //                      {'minute': 'numeric'},
  //                      {'minute': '2-digit'},
  //                      {'second': 'numeric'},
  // {'second': '2-digit'},

  // {'year': 'numeric', 'minute': '2-digit'},
  // {'year': '2-digit', 'minute': 'numeric'},
  // {'year': 'numeric', 'minute': 'numeric'},
  // {'year': '2-digit', 'minute': '2-digit'},

  {'month': 'numeric', 'weekday': 'long', 'day': 'numeric'},
  {'month': '2-digit', 'weekday': 'long', 'day': 'numeric'},
  {'month': 'long', 'weekday': 'long', 'day': 'numeric'},
  {'month': 'short', 'weekday': 'long', 'day': 'numeric'},
  {'month': 'narrow', 'weekday': 'long', 'day': 'numeric'},

  {'month': 'short', 'weekday': 'short', 'day': 'numeric'},
  {'month': 'short', 'weekday': 'narrow', 'day': 'numeric'},

  // TODO: remove non-semantic skeletons
  {'era': 'long'},
  {'era': 'short'},
  {'era': 'narrow'},
  {'timeZoneName': 'long'},
  {'timeZoneName': 'short'},
  {'timeZoneName': 'shortOffset'},
  {'timeZoneName': 'longOffset'},
  {'timeZoneName': 'shortGeneric'},
  {'timeZoneName': 'longGeneric'},
];

const timezones = [
  '',  // Default to UTC
  'America/Los_Angeles',
  'Africa/Luanda',
  'Asia/Tehran',
  'Europe/Kiev',
  'Australia/Brisbane',
  'Pacific/Palau',
  "America/Montevideo"
];

const pre_gregorian_dates = [
  new Date('1066, December 16, 7:17'),  // Expect Sunday
  new Date('1454, May 29, 16:47'),  // Expect Monday
  new Date('BCE 753, April 21'),  // Expect Tuesday
  new Date(0),
  new Date(-1e13),
];

const dates = [
  new Date('Mar 17, 2024'),
  new Date('02-Jul-2001, 13:14:15'),
  new Date('May 29, 1984, 7:53'),
  new Date('2050, May 29, 16:47'),
  new Date('1969, July 16'),
  new Date(1e9),
  new Date(1e12),
];

let temporal_dates = [
  {
    timeZone: 'America/Los_Angeles',
    year: 2024,
    month: 3,
    day: 7,
    hour: 0,
    minute: 0,
    second: 1,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0,
    calendar: "gregory"
  },
  {
    timeZone: 'America/Los_Angeles',
    year: 2001,
    month: 7,
    day: 2,
    hour: 13,
    minute: 14,
    second: 15,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0
  },
  {
    timeZone: 'America/Los_Angeles',
    year: 1984,
    month: 5,
    day: 29,
    hour: 7,
    minute: 53,
    second: 0,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0
  },
  {
    timeZone: 'America/Los_Angeles',
    year: 2030,
    month: 5,
    day: 29,
    hour: 16,
    minute: 47,
    second: 0,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0
  },
  {
    timeZone: 'America/Los_Angeles',
    year: 1969,
    month: 7,
    day: 16,
    hour: 0,
    minute: 0,
    second: 0,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0
  },
  {  // 1e9
    timeZone: 'America/Los_Angeles',
    year: 1970,
    month: 1,
    day: 12,
    hour: 13,
    minute: 46,
    second: 40,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0
  },
  {  // 1e12
    timeZone: 'America/Los_Angeles',
    year: 2001,
    month: 9,
    day: 9,
    hour: 1,
    minute: 46,
    second: 40,
    millisecond: 0,
    microsecond: 0,
    nanosecond: 0
  }
];

const dt_fields = {
  'era': {
    'long': 'GGGG',
    'short': 'GG',
    'narrow': 'GGGGG'
  },
  'year': {
    'numeric': 'y',
    '2-digit': 'yy'
  },
  'quarter': {
    'numeric': 'q'
  },
  'month': {
    'numeric': 'M',
    '2-digit': 'MM',
    'long': 'MMMM',
    'short': 'MMM',
    'narrow': 'MMMMM'
  },
  'weekday': {
    'long': 'EEEE',
    'short': 'E',
    'narrow': 'EEEEE'
  },
  'day': {
    'numeric': 'd',
    '2-digit': 'dd'
  },
  'hour': {
    'numeric': 'j',
    // '2-digit': 'jj'  // Note that this should not be modified
  },
  'minute': {
    'numeric': 'm',
    //  '2-digit': 'mm'
  },
  'second': {
    'numeric': 's',
    //    '2-digit': 'ss'
  },
  'fractionalSecondDigits': {
    1:'S', 2:'SS', 3:'SSS'},
  'timeZoneName': {
    'short': 'z',
    'long': 'zzzz',
    'shortOffset': 'O',
    'longOffset': 'OOOO',
    'shortGeneric': 'v',
    'longGeneric': 'vvvv'}
};

function optionsToSkeleton(options) {
  let skeleton_array = [];

  for (const option of Object.keys(options)) {
    // Look up the symbol
    if (option == 'dateStyle' || option == 'timeStyle')  {
      continue;
    }
    if (dt_fields[option]) {
      const symbol = dt_fields[option];
      const size = options[option];
      // TODO: Get the correct number of symbols.
      if (size in symbol) {
        skeleton_array.push(symbol[size]);
      } else {
        console.warn('#### No entry for ', symbol, ' / ', size);
      }
    }
    else {
      console.warn('# !! No date/time field for this options: ', option, ' in ', options);
    }
  }

  return skeleton_array.join('');
}

function generateAll(run_limit) {

  let test_obj = {
    'Test scenario': 'datetime_fmt',
    'test_type': 'datetime_fmt',
    'description': 'date/time format test data generated by Node',
    'platformVersion': process.version,
    'icuVersion': process.versions.icu,
    'cldrVersion': process.versions.cldr
  };

  let test_cases = [];

  let verify_obj = {
    'test_type': 'datetime_fmt',
    'description': 'date/time format test data generated by Node',
    'platformVersion': process.version,
    'icuVersion': process.versions.icu,
    'cldrVersion': process.versions.cldr
  }
  let verify_cases = [];

  let label_num = -1;  // Increment before each item

  const expected_count = locales.length *
        calendars.length *
        spec_options.length *
        timezones.length *
        dates.length;

  console.log("Generating ", expected_count, " date/time tests for ", process.versions.icu);
  console.log('  RUN LIMIT = ', run_limit);

  for (const locale of locales) {

    const intl_locale = new Intl.Locale(locale);

    for (const calendar of calendars) {

      if ( !skip_things) {
        try {
          const supported_calendars = intl_locale.calendars;
          // Check if the calendar system is supported in this locale.
          // If not, skip the test.
          if (!supported_calendars || !supported_calendars.includes(calendar)) {
            console.
                continue;
          }
        } catch(error) {
          console.log('Supported calendars for %sError: %s',
                      intl_locale, error);
        }
      }
      for (const option of spec_options) {

        if ('era' in option && calendar == 'chinese') {
          // Chinese calendar doesn't have era.
          continue;
        }

        // Rotate timezones through the data, but not as as separate loop
        const tz_index = (label_num + 1) % timezones.length;
        let timezone = timezones[tz_index];


        // Set number systems as appropriate for particular locals
        let number_system = 'latn';
        if (calendar != 'chinese') {
          number_system = 'latn';
        }

        if (locale == 'ar') {
          number_system = 'arab';
        } else
        if (locale == 'bn') {
          number_system = 'beng';
        }

        const skeleton = optionsToSkeleton(option);

        // Create format object with these options
        let all_options = {...option};
        if (calendar != '') {
          all_options['calendar'] = calendar;
        }

        if (timezone) {
          all_options['timeZone'] = timezone;
        } else {
          // Default to GMT+00:00
          all_options['timeZone'] = 'UTC'
          timezone = 'UTC';
        }

        if (number_system) {
          // getNumberingSystems() may not be available yet.
          // If we have this info and the number system isn't in this local, skip the test.
          try {
            const common_number_systems = intl_locale.getNumberingSystems();
            if ((common_number_systems != undefined) &&
                (! common_number_systems.includes(number_system))) {
              console.log('Num system: Skipping ' + number_system +
                          ' in locale' + locale);
              continue;
            }
          } catch(error) {
            // getNumberingSystems isn't implemented. Don't skip.
          }

          all_options['numberingSystem'] = number_system;
        }

        try {
          const supported_calendars = intl_locale.getCalendars();
          if ( !supported_calendars.includes(calendar)) {
            console.warn(locale + ' does not support ' +  calendar);
            console.log(locale + ': ' + supported_calendars);
            continue;
          }
        } catch (error) {
          // geCalendars isn't implemented. Don't skip.
        }

        let formatter;
        try {
          formatter = new Intl.DateTimeFormat(locale, all_options);
        } catch (error) {
          console.error(error, ' with locale ',
                        locale, ' and options: ', all_options);
          continue;
        }

        // Generate this for several actual dates.
        for (const date_index in dates) {
          label_num ++;

          let this_date = dates[date_index];

          // Get the temporal representation, including TZ and calendar
          let temporal_date = temporal_dates[date_index];
          temporal_date['timeZone'] = timezone;

          try {
            let vanilla_locale = 'en-US';
            let vanilla_calendar = 'gregory';
            // temporal_date['calendar'] = vanilla_calendar;

            // For computing the string with Date
            let zdt_vanilla = Temporal.ZonedDateTime.from(temporal_date);
            try {
              this_date = new Date(zdt_vanilla.epochMilliseconds);
            } catch (error) {
              console.log('new Date fail %s with %s on %s', error,
                          temporal_date);
              continue;
            }
            if (! this_date) {
              console.log('$$$$ %s no date from zdt_to_date. %s, %s %s %s',
                          label_num, zdt_vanilla, temporal_date,
                          vanilla_locale, vanilla_calendar);
              continue;
            }
          } catch (error) {
            console.log(' SKIPPING %s temporal.from %s: input: %s',
                        label_num, error, temporal_date);
            continue;
          }

          // Get the ISO string with
          // temporal_date['calendar'] = calendar;
          let zdt_full = Temporal.ZonedDateTime.from(temporal_date);
          input_string = zdt_full.toString();

          // !! TEMPORARY !!
          // console.log(' TEMPORAL %s %s %s', label_num, input_string, this_date);

          let result;
          let parts;
          try {
            // To avoid the hack that replaces NBSP with ASCII space.
            try {
              parts = formatter.formatToParts(this_date);
            } catch (error) {
              console.log('!!!!!! %s %s', label_num, error);
              console.log('      temporal_data = %s', temporal_date)
              console.log('       %s formatToParts with %s', error, this_date);
              continue;
            }
            // Handle options that have only era or timeZoneName, working around
            // https://github.com/tc39/ecma402/issues/461
            const keys = Object.keys(option);

            if (keys.length == 1 &&
                (keys[0] == 'era' || keys[0] == 'timeZoneName')) {
              if (calendar == 'chinese') {
                continue;
              }
              try {
                const item = parts.filter(({type}) => type === keys[0]);
                try {
                  result = item[0]['value'];
                } catch(error) {
                  // This item isn't in the output. Just return the entire string.
                  result = parts.map((x) => x.value).join("");
                }
                if (!result || debug) {
                  console.log('OK!  key = %s, %s',
                              keys[0],
                              JSON.stringify(all_options));
                  console.log('  ITEM = ', JSON.stringify(item))
                  console.log('  PARTS = ', JSON.stringify(parts));
                }

              } catch (error) {
                console.error('PARTS FILTER error: %s, key = ',
                              error, keys[0], this_date);
                console.error('     %s' + JSON.stringify(parts));
                console.error('     %s' + JSON.stringify(all_options));
              }

            } else {
              // Not era or timeZoneName
              result = parts.map((x) => x.value).join("");
              if (!result) {
                console.warn('no result for ', label_num, ': ', JSON.stringify(all_options));
              }
            }

          } catch (error) {
            console.error('FORMATTER result fails! ', error);
            const keys = Object.keys(all_options);
            console.error('  options: ' + locale + ", " + keys);
            console.error('    ' + JSON.stringify(all_options));
          }
          // format this date
          // get the milliseconds
          const millis = this_date.getTime();

          const label_string = String(label_num);

          let test_case = {
            'input_string': input_string
          };

          if (skeleton) {
            test_case['skeleton'] = skeleton;
          }

          if (use_milliseconds) {
            // Optional
            test_case['input_millis'] = millis;
          }

          if (locale != '') {
            test_case["locale"] = locale;
          }
          if (all_options != null) {
            test_case["options"] = {...all_options};
          }

          if (!result || debug) {
            console.debug("TEST CASE :", test_case);
          }

          gen_hash.generate_hash_for_test(test_case);

          test_case['label'] = label_string;

          test_cases.push(test_case);

          // Generate what we get.
          try {
            if (!result) {
              console.warn('NO RESULT: ', label_string);
            }
            verify_cases.push({'label': label_string,
                               'verify': result});
            if (debug) {
              console.log('   expected = ', result);
            }
          } catch (error) {
            console.error('!!! error ', error, ' in label ', label_num,
                          ' for date = ', d);
          }
        }
        // !!!
        // console.log('');
      }
    }
  }


  test_obj['tests'] = sample_tests(test_cases, run_limit);
  try {
    fs.writeFileSync('datetime_fmt_test.json', JSON.stringify(test_obj, null));
    // file written successfully
  } catch (err) {
    console.error(err);
  }

  console.log('Number of date/time sampled tests for version ',
              process.versions.icu, ': ', test_obj['tests'] .length);

  verify_obj['verifications'] = sample_tests(verify_cases, run_limit);
  try {
    fs.writeFileSync('datetime_fmt_verify.json', JSON.stringify(verify_obj, null, 2));
    // file written successfully
  } catch (err) {
    console.error(err);
  }
}

function sample_tests(all_tests, run_limit) {
  // Gets a sampling of the data based on total and the expected number.

  if (run_limit < 0 || all_tests.length <= run_limit) {
    return all_tests;
  }

  let size_all = all_tests.length;
  let increment = Math.floor(size_all / run_limit);
  let samples = [];
  for (let index = 0; index < size_all; index += increment) {
    samples.push(all_tests[index]);
  }
  return samples;
}

/* Call the generator */
let run_limit = -1;
if (process.argv.length >= 5) {
  if (process.argv[3] == '-run_limit') {
    run_limit = Number(process.argv[4]);
  }
}

// Call the generator
generateAll(run_limit);
