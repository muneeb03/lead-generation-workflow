# Automated Lead Generation Workflow

A comprehensive Python tool for automated lead generation across multiple platforms. This tool allows you to collect business, personal, and institutional leads based on industry and location parameters.

## 🌟 Features

- **Multi-source data collection**: Scrapes leads from over 15 different platforms
- **Flexible lead types**: Business, personal, and institutional 
- **Parallel processing**: Collect data from multiple sources simultaneously
- **Proxy rotation**: Avoid IP blocking during web scraping
- **Multiple export formats**: Excel (with multiple sheets), CSV, and JSON
- **Configurable**: Extensive command-line options for customization

## 📋 Lead Sources

### Business Leads
- Google Maps
- Yelp
- Yellow Pages
- Better Business Bureau
- Chambers of Commerce
- Indeed

### Personal/Contact Leads
- LinkedIn
- ZoomInfo
- Hunter.io
- Apollo.io
- Clearbit

### Institutional Leads
- Government Websites
- Association Directories
- Guidestar/Candid
- Charity Navigator
- Educational Directories

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/muneeb03/lead-generation-workflow.git
cd lead-generation-workflow
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Download and install ChromeDriver:
   - Visit https://sites.google.com/chromium.org/driver/
   - Download the appropriate version for your Chrome browser
   - Add the ChromeDriver to your system PATH

## 🔧 Usage

### Basic Usage

```bash
python lead_generation.py --industry "restaurants" --location "Chicago"
```

### Advanced Usage

```bash
python lead_generation.py \
  --industry "software development" \
  --location "San Francisco" \
  --type business \
  --count 100 \
  --sources google_maps yelp better_business_bureau \
  --parallel \
  --export-format all \
  --output sf_software_leads \
  --delay 2.0
```

### Command-line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--industry` | Industry to search for | *Required* |
| `--location` | Location to search in | *Required* |
| `--type` | Type of leads (business, personal, institutional) | `business` |
| `--count` | Number of leads to generate | `50` |
| `--output` | Output filename | `leads.xlsx` |
| `--sources` | Specific sources to search | *Based on type* |
| `--parallel` | Enable parallel processing | `False` |
| `--proxy` | Proxy to use for web requests | `None` |
| `--delay` | Delay between requests (seconds) | `1.0` |
| `--export-format` | Export format (excel, csv, json, all) | `excel` |

## 🔑 API Keys

Some data sources require API keys for full functionality:

1. Create a `.env` file in the project root:
```
HUNTER_IO_API_KEY=your_hunter_io_key
CLEARBIT_API_KEY=your_clearbit_key
APOLLO_IO_API_KEY=your_apollo_io_key
ZOOMINFO_API_KEY=your_zoominfo_key
```

2. Load environment variables:
```bash
source .env  # On Windows, use: set -a; . .env; set +a
```

## 🔄 Proxy Support

For improved reliability and to avoid rate limiting:

1. Create a `proxies.txt` file with one proxy per line:
```
http://user:pass@proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
```

2. Use the `--proxy` flag or set the `PROXY_LIST` environment variable.

## 📊 Example Output

The tool creates Excel files with multiple sheets:

1. **All Leads** - Combined data from all sources
2. One sheet per source (Google Maps, Yelp, etc.)

Each lead typically includes:
- Name/Organization
- Contact information (email, phone)
- Address
- Website
- Industry-specific details
- Source metadata

## ⚠️ Legal Considerations

**Important**: Web scraping may violate terms of service for some websites. This tool is for educational purposes only. Always:

1. Review and respect each website's robots.txt file
2. Implement appropriate rate limiting
3. Consider using official APIs when available
4. Ensure compliance with local laws regarding data collection and privacy

## 🔍 Customization

### Adding New Sources

1. Create a new method in the `LeadGenerationAgent` class:
```python
def search_new_source(self, industry, location, lead_count=20):
    # Implementation here
    pass
```

2. Add the source to the appropriate category in `self.sources`.

## 🛠️ Troubleshooting

### Common Issues

1. **Selenium errors**: Ensure ChromeDriver is compatible with your Chrome version
2. **Rate limiting**: Increase the delay between requests with `--delay`
3. **IP blocking**: Use the proxy rotation feature with `--proxy`
4. **Missing data**: Some fields may be unavailable from certain sources

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
