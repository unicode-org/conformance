macro_rules! try_or_return_error {
	($label:expr, $locale:expr, $expr:expr) => {{
		match ($expr) {
			Ok(x) => x,
			Err(e) => {
				return Ok(json!({
					"label": ($label),
					"locale_label": ($locale).to_string(),
					"error": e.to_string(),
					"error_type": "panic",
				}));
			}
		}
	}};
}

pub(crate) use try_or_return_error;
