# Featureswitches

A Python package for interacting with [FeatureSwitches.com](https://featureswitches.com).  This library is under active development and is likely to change frequently.  Bug reports and pull requests are welcome.

## Installation

```bash
pip install featureswitches
```

## Usage

```python
fs = FeatureSwitches('customer_api_key', 'environment_api_key')

# Ensure that the API credentials are valid
result = fs.authenticate()  # result will be true/false to indicate success

# Add a user
result = fs.add_user('user_identifier', 'optional_customer_identifier', 'optional_name', 'optional_email')

# Check if a feature is enabled
result = fs.is_enabled('feature_key', 'optional_user_identifier', default_return_value(true/false, default=false))

if result:
    # Feature enabled, do something
else:
    # Feature disabled, do something else
```

### Configuration Options
A few options are available to be tweaked if you so choose. The library makes use of a local cache to minimize requests back to the FeatureSwitches server. Additionally, a check it performed at an interval to automatically re-sync feature state when changes are made in the dashboard.

* cache_timeout=SECONDS   # Defaults to 300 seconds
* check_interval=SECONDS  # Defaults to 10 seconds

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/featureswitches/featureswitches-python.


## License

The library is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).

