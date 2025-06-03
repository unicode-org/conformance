/* Generate segmenter test data with the following dimensions:

   1. locale
   2. granularity
*/

// Set up Node version to generate data specific to ICU/CLDR version
// e.g., `nvm install 21.6.0;nvm use 21.6.0` (ICU 74)

const common_fns = require("./common.js");
const gen_hash = require("./generate_test_hash.js");

const fs = require('node:fs');

let debug = false;

const test_type = "segmenter";

const granularity = ['grapheme', 'word', 'sentence', 'line'];

// Expected results for line breaks are hard coded because NodeJS does not
// yet support this granularity.
const locale_text_data = [
  {
    // Empty input
    "locale": "en-US",
    "input": "",
    'expected_line_results': []
  },

  {
    "locale": "en-US",
    "input": "The cât, in the hat. There's a dog̈ in the yard?",
    'expected_line_results': ["The ","cât, ","in ","the ","hat. ","There's ","a ","dog̈ ","in ","the ","yard?"]
  },
  {
    "locale": "ja-JP",
    "input": "文字に分解しましょう。単語にも。ああ、文にも。",
    'expected_line_results': ["文","字","に","分","解","し","ま","しょ","う。","単","語","に","も。","あ","あ、","文","に","も。"]
  },
  {
    "locale": "fr",
    "input": "C'est ainsi qu'on décompose les personnages. Les mots aussi. Oh, et les phrases aussi.",
    'expected_line_results': ["C'est ","ainsi ","qu'on ","décompose ","les ","personnages. ","Les ","mots ","aussi. ","Oh, ","et ","les ","phrases ","aussi."]
  },
  {
    "locale": "as",
    "input": "এইটোৱেই হৈছে চৰিত্ৰত ভাঙি যোৱাৰ উপায়। লগতে শব্দ। অ’, আৰু বাক্যবোৰো।",
    'expected_line_results': ["এইটোৱেই ","হৈছে ","চৰিত্ৰত ","ভাঙি ","যোৱাৰ ","উপায়। ","লগতে ","শব্দ। ","অ’, ","আৰু ","বাক্যবোৰো।"]
  },
  {
    "locale": "zh-Hans",
    "input": "分解成字符。还有单词。哦，还有句子。",
    'expected_line_results': ["分","解","成","字","符。","还","有","单","词。","哦，","还","有","句","子。"]
  },
  {
    "locale": "zh-Hant",
    "input": "分解成字元。還有文字。哦，還有句子。",
    'expected_line_results': ["分","解","成","字","元。","還","有","文","字。","哦，","還","有","句","子。"]
  },
  {
    "locale": "my",
    "input": "ဤသည်မှာ ဇာတ်ကောင်များအဖြစ်သို့ ဖောက်ထွက်ရန် နည်းလမ်းဖြစ်သည်။ စကားလည်း ပါတယ်။ သြော် စာကြောင်းတွေလည်း ပါပါတယ်။",
    'expected_line_results': ["ဤ","သည်မှာ ","ဇာတ်ကောင်","များ","အဖြစ်","သို့ ","ဖောက်","ထွက်","ရန် ","နည်း","လမ်း","ဖြစ်သည်။ ","စကား","လည်း ","ပါ","တယ်။ ","သြော် ","စာကြောင်း","တွေ","လည်း ","ပါ","ပါ","တယ်။"]
  },
  {
    "locale": "ff-Adlm",
    "input": "𞤊𞤭𞤴𞤢𞥄𞤳𞤵 𞤱𞤢𞤴𞤤𞤮𞤪𞤢 𞤳𞤫𞤲𞤫𞤲. 𞤖𞤢𞤳𞥆𞤫𞤪𞤫𞤲 𞤫𞤯𞤫𞤲 𞤸𞤮𞥅𞤤𞤭𞥅  𞤸𞤭𞤧𞤭⹁ 𞤫𞤲𞤢 𞤯𞤫𞤲. 𞤐𞤣𞤫𞤲𞤧𞤢𞤴 𞤼𞤵𞤲⹁ 𞤭𞤱𞤪𞤢𞤼𞤢 𞤱𞤮𞥅⹁ 𞤣𞤫𞥅𞤰𞤵𞤲𞤮𞥅 𞤬𞤮𞤱⹁ 𞤮𞤲.",
    'expected_line_results': ["𞤊𞤭𞤴𞤢𞥄𞤳𞤵 ","𞤱𞤢𞤴𞤤𞤮𞤪𞤢 ","𞤳𞤫𞤲𞤫𞤲. ","𞤖𞤢𞤳𞥆𞤫𞤪𞤫𞤲 ","𞤫𞤯𞤫𞤲 ","𞤸𞤮𞥅𞤤𞤭𞥅  ","𞤸𞤭𞤧𞤭⹁ ","𞤫𞤲𞤢 ","𞤯𞤫𞤲. ","𞤐𞤣𞤫𞤲𞤧𞤢𞤴 ","𞤼𞤵𞤲⹁ ","𞤭𞤱𞤪𞤢𞤼𞤢 ","𞤱𞤮𞥅⹁ ","𞤣𞤫𞥅𞤰𞤵𞤲𞤮𞥅 ","𞤬𞤮𞤱⹁ ","𞤮𞤲."]
  },
  {
    "locale": "ar",
    "input": "لنبحث عن نقاط توقف محتملة. في هذه البيانات؟",
    "expected_line_results": ["لنبحث ","عن ","نقاط ","توقف ","محتملة. ","في ","هذه ","البيانات؟"]
  },
  {
    "locale": "bo",
    "input": "འབྱུང་སྲིད་པའི་བར་ཆད་ཀྱི་ས་ཚིགས་འཚོལ་རོགས། གཞི་གྲངས་འདིའི་ནང་དུ།",
    "expected_line_results": ["འབྱུང་","སྲིད་","པའི་","བར་","ཆད་","ཀྱི་","ས་","ཚིགས་","འཚོལ་","རོགས། ","གཞི་","གྲངས་","འདིའི་","ནང་","དུ།"]
  },
  {
    "locale": "ta",
    "input": "சாத்தியமான முறிவுப் புள்ளிகளைக் கண்டுபிடிப்போம். இந்தத் தரவில்?",
    "expected_line_results": ["சாத்தியமான ","முறிவுப் ","புள்ளிகளைக் ","கண்டுபிடிப்போம். ","இந்தத் ","தரவில்?"]
  },
  {
    "locale": "be-Tfng",
    "input": "ⴰⴷ ⵏⴰⴼ ⵜⵉⵏⴻⵇⵇⵉⴹⵉⵏ ⵏ ⵜⴽⴻⵔⴽⴰⵙ ⵉⵣⴻⵎⵔⴻⵏ ⴰⴷ ⵉⵍⵉⵏⵜ. ⴷⴻⴳ ⵢⵉⵙⴻⴼⴽⴰⴰ?",
    "expected_line_results": ["ⴰⴷ ","ⵏⴰⴼ ","ⵜⵉⵏⴻⵇⵇⵉⴹⵉⵏ ","ⵏ ","ⵜⴽⴻⵔⴽⴰⵙ ","ⵉⵣⴻⵎⵔⴻⵏ ","ⴰⴷ ","ⵉⵍⵉⵏⵜ. ","ⴷⴻⴳ ","ⵢⵉⵙⴻⴼⴽⴰⴰ?"]
  },
  {
    "locale": "qu",
    "input": "Atikuq p’akisqa puntokunata maskhasun. ¿Kay datospi?",
    "expected_line_results": ["Atikuq ","p’akisqa ","puntokunata ","maskhasun. ","¿Kay ","datospi?"]
  },
  {
    "locale": "am",
    "input": "ሊሆኑ የሚችሉ የእረፍት ነጥቦችን እንፈልግ። በዚህ ውሂብ ውስጥ?",
    "expected_line_results": ["ሊሆኑ ","የሚችሉ ","የእረፍት ","ነጥቦችን ","እንፈልግ። ","በዚህ ","ውሂብ ","ውስጥ?"]
  },


];

function generateAll() {

  let test_obj = {
    'test_type': test_type,
    'description': 'Segmenter test data generated by NodeJS',
    'platformVersion': process.version,
    'icuVersion': process.versions.icu,
    'cldrVersion': process.versions.cldr
  };

  let test_cases = [];

  let verify_obj = {
    'test_type': test_type,
    'description': 'segmenter expected resuls generated by NodeJS',
    'platformVersion': process.version,
    'icuVersion': process.versions.icu,
    'cldrVersion': process.versions.cldr
  }
  let verify_cases = [];

  let label_num = 0;

  const expected_count = locale_text_data.length * granularity.length;

  console.log("Generating up to ", expected_count, " segmenter tests for ",
              process.versions.icu);

  for (const locale_data of locale_text_data) {

    const locale = locale_data['locale'];
    for (const segmentation_type of granularity) {

      // Create format object with these options
      let all_options = {};
      if (segmentation_type == 'line') {
        // To get line data, even though not supported in ECMA Intl
        all_options['granularity'] = 'word';
      } else {
        all_options['granularity'] = segmentation_type;
      }

      let segmenter;
      try {
        segmenter = new Intl.Segmenter(locale, all_options);
      } catch (error) {
        console.log(error, ' with locale ',
                    locale, ' and options: ', all_options);
        continue;
      }

      const input = locale_data['input'];
      let result = [];
      try {
        const iterator = segmenter.segment(input)[Symbol.iterator]();
        let seg_item = iterator.next();
        while (! seg_item.done) {
          result.push(seg_item.value.segment);
          seg_item = iterator.next();
        }
      } catch (error) {
        console.log('SEGMENTER FAIL! ', error);
      }
      const label_string = String(label_num);

      if (segmentation_type == 'grapheme') {
        all_options['granularity'] = 'grapheme_cluster';
      }
      let test_list;
      let test_case = {
        "locale": locale,
        "options": all_options,
        "input": input
      };
      gen_hash.generate_hash_for_test(test_case);
      test_case['label'] = label_string;

      if (debug) {
        console.log("TEST CASE :", test_case);
      }
      if (segmentation_type == 'line') {
        // To get line data, even though not supported in ECMAIntl
        all_options['granularity'] = 'line';
      }
      test_cases.push(test_case);

      // Generate what we get.
      if (segmentation_type == 'line') {
        result = locale_data['expected_line_results'];
      }
      try{
        verify_cases.push({'label': label_string,
                           'verify': result});
      } catch (error) {
        console.log('!!! error ', error, ' in label ', label_num,
                    ' for options ', options);
      }
      label_num ++;
    };
  }

  if (debug) {
    console.log('Number of segmenter tests generated for ',
                process.versions.icu, ': ', label_num);
    console.log(' RUN LIMIT = ', run_limit);
  }

  test_obj['tests'] = common_fns.sample_tests(test_cases, run_limit);
  try {
    fs.writeFileSync('segmenter_test.json', JSON.stringify(test_obj, null));
    // file written successfully
  } catch (err) {
    console.error(err);
  }

  verify_obj['verifications'] = common_fns.sample_tests(verify_cases, run_limit);
  try {
    fs.writeFileSync('segmenter_verify.json', JSON.stringify(verify_obj, null));
    // file written successfully
  } catch (err) {
    console.error(err);
  }
}

if (debug) {
  console.log('SEGMENTER argv: ', process.argv);
}

let run_limit = -1;
if (process.argv.length >= 4) {
  if (process.argv[2] == '-run_limit') {
    run_limit = Number(process.argv[3]);
  }
}

/* Call the generator */
generateAll(run_limit);
