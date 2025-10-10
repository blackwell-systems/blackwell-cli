# Getting Started with Blackwell CLI

A step-by-step guide to get you up and running with the Blackwell CLI for composable web stack deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Your First Project](#your-first-project)
- [Understanding Costs](#understanding-costs)
- [Next Steps](#next-steps)

## Prerequisites

### Required Software

Before installing Blackwell CLI, ensure you have:

1. **Python 3.13+**
   ```bash
   python --version  # Should show 3.13 or higher
   ```

2. **uv Package Manager**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Verify installation
   uv --version
   ```

3. **AWS CLI** (configured)
   ```bash
   # Install AWS CLI
   # See: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

   # Configure AWS credentials
   aws configure

   # Test configuration
   aws sts get-caller-identity
   ```

4. **AWS CDK CLI**
   ```bash
   # Install Node.js first (if not installed)
   # Then install CDK globally
   npm install -g aws-cdk

   # Verify installation
   cdk --version
   ```

### AWS Account Setup

You'll need:
- An AWS account with appropriate permissions
- AWS credentials configured (via `aws configure` or environment variables)
- A default region set (recommended: `us-east-1`)

### Platform-Infrastructure Project

The Blackwell CLI integrates with the [platform-infrastructure](../platform-infrastructure) project:
- Clone or download the platform-infrastructure repository
- The CLI can auto-discover it in common locations
- Or you can specify the path manually during setup

## Installation

### Method 1: Development Installation (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd blackwell-cli

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .

# Verify installation
blackwell --version
```

### Method 2: Direct Installation (Future)

```bash
# When published to PyPI (future)
uv pip install blackwell-cli
blackwell --version
```

## Initial Setup

### 1. Initialize Your Workspace

Run the interactive workspace setup:

```bash
blackwell init workspace
```

This will guide you through:

#### AWS Configuration
```
AWS Configuration
AWS Profile [default]:
AWS Region [us-east-1]:
```

#### Platform-Infrastructure Integration
```
Platform-Infrastructure Integration
Platform-infrastructure path [auto-discover]:
```

The CLI will auto-discover platform-infrastructure in:
- `./platform-infrastructure`
- `../platform-infrastructure`
- `~/code/business/platform-infrastructure`

#### Default Preferences
```
Default Preferences
CMS Provider Options: decap, tina, sanity, contentful
Default CMS Provider [decap]:

E-commerce Provider Options: snipcart, foxy, shopify_basic
Default E-commerce Provider [snipcart]:

SSG Engine Options: hugo, eleventy, astro, gatsby, nextjs, nuxtjs
Default SSG Engine [astro]:

Integration Mode Options: direct, event_driven
Default Integration Mode [event_driven]:
```

### 2. Verify Configuration

The setup will validate your configuration:

```
✓ Configuration valid
✓ Platform-infrastructure found at: /path/to/platform-infrastructure
✓ AWS configuration valid
✓ CDK CLI available
```

If issues are found, you'll see troubleshooting tips:

```
⚠ Configuration Issues Found:
• Platform-infrastructure project not found or invalid
• AWS configuration invalid: NoCredentialsError

Would you like to see troubleshooting tips? [y/N]: y
```

## Your First Project

### Interactive Project Creation

Create your first project with guided setup:

```bash
blackwell init project my-startup --interactive
```

### Step-by-Step Walkthrough

#### 1. Project Information
```
📋 Client Information
Company Name: My Startup Co
Primary Domain [mystartup.com]:
Contact Email: admin@mystartup.com
Monthly Budget (USD) [no-limit]: 100
```

#### 2. Budget Analysis
```
💰 Budget Analysis (Target: $100/month)
Based on your budget, here are the recommended provider combinations:

1. 🥇 Decap + Snipcart + Astro: $89/month ✅
   • FREE CMS (git-based content management)
   • $29/month e-commerce + 2% transaction fees
   • $60/month AWS hosting
   • Best for: Technical teams, budget-conscious startups

2. 🥈 Tina + Snipcart + Astro: $118/month ⚠️ (18% over budget)
   • $29/month visual CMS
   • $29/month e-commerce + 2% transaction fees
   • $60/month AWS hosting
   • Best for: Non-technical content editors

Recommendation: Option 1 (Decap + Snipcart + Astro)
```

#### 3. Integration Mode Selection
```
🎯 Integration Mode:
• Direct Mode: Simple, lower cost ($89/month)
• Event-Driven Mode: Composition-ready, future flexibility ($104/month)

Recommendation: Event-Driven (better long-term flexibility for +$15/month)
```

#### 4. Configuration Summary
```
📋 Configuration Summary:
• CMS: Decap CMS (FREE, git-based)
• E-commerce: Snipcart (2% transaction fees)
• SSG Engine: Astro (modern, fast)
• Integration: Event-Driven (composition-ready)
• Monthly Cost: $104/month + 2% of sales
• Stack Name: MyStartup-Prod-DecapSnipcartComposedStack

Create this configuration? [y/N]: y
```

#### 5. Cost Breakdown
```
💰 Cost Estimation
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component           ┃ Monthly Cost ┃ Notes                                    ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ CMS Provider        │ $0.00        │ Content management                       │
│ E-commerce Provider │ $29.00       │ Online store platform                   │
│ AWS Hosting         │ $45.00       │ Infrastructure hosting                   │
│ Event Infrastructure│ $15.00       │ Composition features                     │
│ Data Transfer       │ $5.00        │ CDN and bandwidth                        │
│ Storage             │ $5.00        │ File and asset storage                   │
│                     │              │                                          │
│ Total Fixed Cost    │ $99.00       │ Monthly fixed costs                      │
└─────────────────────┴──────────────┴──────────────────────────────────────────┘
Transaction Fees                      2.0%             Per-sale variable cost

Cost Tier: Budget
```

#### 6. Success and Next Steps
```
✅ Project 'my-startup' created successfully!

Next Steps:
  • blackwell deploy client my-startup --preview
  • blackwell cost estimate my-startup
  • blackwell list clients
```

## Understanding Costs

### Cost Components

Your monthly cost consists of:

1. **CMS Provider Cost**: $0-300+ depending on provider choice
2. **E-commerce Provider Cost**: $29-75+ base cost
3. **AWS Infrastructure Cost**: $45-75 for hosting and CDN
4. **Transaction Fees**: 1.5-2.9% of sales (variable)

### Cost Tiers

- **Budget**: Under $100/month (Decap + Snipcart)
- **Standard**: $100-250/month (Tina/low-tier Sanity + Snipcart)
- **Professional**: $250-500/month (Sanity + Foxy or Shopify)
- **Enterprise**: $500+/month (Contentful + Shopify)

### Example Cost Scenarios

#### Scenario 1: Budget Startup ($89/month + 2% fees)
```
• CMS: Decap (FREE)
• E-commerce: Snipcart ($29)
• AWS: $60
• Transaction fees: 2%
• Best for: Technical teams, minimal budget
```

#### Scenario 2: Growing Business ($158/month + 2% fees)
```
• CMS: Sanity ($99)
• E-commerce: Snipcart ($29)
• AWS: $75 (event-driven)
• Transaction fees: 2%
• Best for: Structured content needs
```

#### Scenario 3: Enterprise ($430/month + 2.9% fees)
```
• CMS: Contentful ($300)
• E-commerce: Shopify Basic ($29)
• AWS: $80 (full features)
• Transaction fees: 2.9%
• Best for: Large teams, complex workflows
```

## Next Steps

### Immediate Actions

1. **Deploy Your Project**
   ```bash
   blackwell deploy client my-startup --preview
   ```

2. **Explore Cost Optimization**
   ```bash
   blackwell cost estimate my-startup
   blackwell cost optimize my-startup
   ```

3. **List Your Projects**
   ```bash
   blackwell list clients
   ```

### Learn More

- **[Provider Selection Guide](provider-guide.md)**: Detailed comparison of CMS and e-commerce providers
- **[Cost Optimization Guide](cost-optimization.md)**: Advanced cost optimization strategies
- **[Migration Guide](migration-guide.md)**: How to migrate between providers
- **[API Reference](api-reference.md)**: Developer documentation and API reference

### Get Help

- **CLI Help**: `blackwell --help` or `blackwell <command> --help`
- **System Diagnostics**: `blackwell doctor`
- **Configuration Issues**: `blackwell config show`

### Common Commands Reference

```bash
# Workspace management
blackwell init workspace                # Initialize CLI workspace
blackwell config show                   # Show current configuration
blackwell doctor                       # Run system diagnostics

# Project management
blackwell init project <name>          # Create new project
blackwell list clients                 # List all projects
blackwell deploy client <name>         # Deploy a project

# Cost analysis
blackwell cost estimate <name>         # Estimate project costs
blackwell cost compare --budget 150    # Compare options within budget
blackwell cost optimize <name>         # Get optimization suggestions

# Templates
blackwell templates list               # Show available templates
blackwell templates apply <template> <client>  # Apply template

# Provider migration
blackwell migrate cms <client> --to sanity     # Migrate CMS provider
blackwell migrate mode <client> --to direct    # Change integration mode
```

## Troubleshooting

### Common Issues

#### 1. "Platform-infrastructure not found"
```bash
# Solution 1: Let CLI auto-discover
blackwell init workspace

# Solution 2: Set path manually
blackwell config set platform_infrastructure.path /path/to/platform-infrastructure
```

#### 2. "AWS configuration invalid"
```bash
# Check AWS credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

#### 3. "CDK CLI not found"
```bash
# Install CDK globally
npm install -g aws-cdk

# Verify installation
cdk --version
```

#### 4. "Permission denied" errors
```bash
# Check AWS permissions
aws iam get-user

# Ensure your user has necessary permissions for:
# - S3, CloudFront, Route53, CodeBuild, Lambda, SNS, DynamoDB
```

### Getting More Help

- Run `blackwell doctor` for comprehensive system diagnostics
- Check the [Migration Guide](migration-guide.md) for advanced troubleshooting
- Review logs with `blackwell --verbose <command>`

---

You're now ready to create and deploy sophisticated web infrastructure with intelligent cost optimization! 🚀