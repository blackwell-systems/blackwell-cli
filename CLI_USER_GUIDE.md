# Blackwell CLI User Guide

**🚀 Simplify composable web stack deployment with intelligent provider selection and live platform integration**

## Table of Contents

- [Overview](#overview)
- [Revolutionary Platform Integration](#revolutionary-platform-integration)
- [Installation & Setup](#installation--setup)
- [Platform Integration Commands](#platform-integration-commands)
- [Core CLI Commands](#core-cli-commands)
- [CDK Bootstrap Management](#cdk-bootstrap-management)
- [System Diagnostics](#system-diagnostics)
- [Provider Management](#provider-management)
- [Configuration System](#configuration-system)
- [Real-World Workflows](#real-world-workflows)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Migration from Static Mode](#migration-from-static-mode)

---

## Overview

Blackwell CLI revolutionizes web development by providing **intelligent provider selection** with **live platform integration**. Create sophisticated multi-client web infrastructure by mixing any CMS (Decap, Tina, Sanity, Contentful) with any E-commerce provider (Snipcart, Foxy, Shopify) using any SSG engine (Hugo, Eleventy, Astro, Gatsby, Next.js, Nuxt.js).

### ✨ **Key Innovations**

**🔗 Live Platform Integration**
- Dynamic provider matrix synchronized with platform-infrastructure
- Real-time stack metadata and capabilities
- Intelligent cost estimation and recommendations
- Graceful fallback to static data when needed

**🛡️ Resilient Architecture**
- Safe import patterns ensure CLI always works
- Multiple control layers (config, environment, CLI flags)
- Rich diagnostics with actionable recommendations
- Zero-downtime platform updates

**💡 Enhanced Intelligence**
- Smart provider compatibility checking
- Automatic cost optimization suggestions
- Live metadata refresh capabilities
- Cross-provider integration insights

---

## Revolutionary Platform Integration

The Blackwell CLI implements a **Stack Unification Plan** that bridges static CLI definitions with live platform-infrastructure data, providing the best of both worlds.

### 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BLACKWELL CLI ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐ │
│  │   CLI Commands  │    │  Configuration   │    │  Provider Matrix    │ │
│  │                 │    │   Management     │    │                     │ │
│  │ • create        │    │                  │    │ ┌─ Dynamic (Live)   │ │
│  │ • deploy        │    │ • Path detection │    │ │  Platform data    │ │
│  │ • platform      │    │ • Smart fallback │    │ │  15+ stack types  │ │
│  │ • cost          │◄───┤ • Multi-layer    │◄───┤ │                   │ │
│  │ • migrate       │    │   control        │    │ └─ Static (Backup)  │ │
│  └─────────────────┘    └──────────────────┘    │    Reliable         │ │
│                                                  │    fallback         │ │
│                                                  └─────────────────────┘ │
│                                   ▲                                     │
│                                   │                                     │
│                          ┌─────────────────┐                            │
│                          │ Safe Import     │                            │
│                          │ Pattern         │                            │
│                          │                 │                            │
│                          │ try:            │                            │
│                          │   from shared   │                            │
│                          │ except:         │                            │
│                          │   graceful_fall │                            │
│                          └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 🎯 **Integration Modes**

**Dynamic Mode (Recommended)**
- Live data from platform-infrastructure
- Enhanced intelligence and recommendations
- Automatic synchronization
- Advanced cost estimation

**Static Mode (Fallback)**
- Self-contained operation
- Zero external dependencies
- Reliable baseline functionality
- Emergency operation capability

---

## Installation & Setup

### Prerequisites

- **Python**: 3.13+ (project requires 3.13)
- **Package Manager**: `uv` (recommended) or `pip`
- **Platform Integration**: Optional platform-infrastructure project

#### **🏗️ AWS CDK Requirements (for deployment)**

- **Node.js**: 18+ (required for AWS CDK)
- **AWS CDK**: 2.x (`npm install -g aws-cdk`)
- **AWS CLI**: 2.x with configured credentials
- **CDK Bootstrap**: Required for deployment (managed by CLI)

### 🚀 **Quick Installation**

```bash
# 1. Install using uv (recommended)
cd blackwell-cli
uv sync

# 2. Install CLI in development mode
uv add --editable .

# 3. (Optional) Add platform-infrastructure for enhanced features
uv add --editable ../platform-infrastructure

# 4. Verify installation
uv run blackwell --version
```

### 🔧 **Platform Integration Setup**

```bash
# Auto-discover platform-infrastructure
blackwell platform path --auto-discover

# Or set manually
blackwell platform path --set /path/to/platform-infrastructure

# Check integration status
blackwell platform status

# Enable dynamic mode
blackwell platform enable

# Verify AWS deployment readiness (including CDK bootstrap)
blackwell doctor --deployment-check
```

**Expected Output:**
```
Platform Integration Status
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component             ┃ Status       ┃ Details                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Platform Availability │ ✓ Available  │ Import successful: dynamic          │
│ Metadata Count        │ ✓ 15 entries │ Stack types available from platform │
└───────────────────────┴──────────────┴─────────────────────────────────────┘
```

---

## Platform Integration Commands

The CLI provides comprehensive platform integration management through the `blackwell platform` command group.

### 📊 **Status & Diagnostics**

```bash
# Comprehensive status check
blackwell platform status

# Detailed diagnostics with verbose output
blackwell platform status --verbose

# Complete integration diagnostics
blackwell platform doctor
```

**Status Components Explained:**
- **Configuration Path**: Location of platform-infrastructure project
- **Path Validation**: Structural verification of platform project
- **Static Mode**: Whether integration is disabled
- **Live Metadata**: Dynamic provider matrix status
- **Environment Override**: `BLACKWELL_FORCE_STATIC` variable status
- **Platform Availability**: Import success and metadata count

### 🔄 **Metadata Management**

```bash
# Refresh platform metadata cache
blackwell platform refresh

# Force refresh even in static mode
blackwell platform refresh --force

# Show available providers and their source
blackwell platform providers

# Show providers from specific source
blackwell platform providers --source platform
blackwell platform providers --source static
```

### ⚙️ **Integration Control**

```bash
# Enable platform integration (dynamic mode)
blackwell platform enable

# Disable platform integration (static mode)
blackwell platform disable

# Manage platform project path
blackwell platform path                    # Show current path
blackwell platform path --set /path/to/platform
blackwell platform path --auto-discover   # Find automatically
```

### 🏥 **Troubleshooting**

```bash
# Run comprehensive diagnostics
blackwell platform doctor

# Check configuration validity
blackwell config show

# Validate system dependencies
blackwell doctor

# Show detailed platform status
blackwell platform status --verbose
```

---

## Core CLI Commands

### 🎬 **Project Initialization**

```bash
# Initialize new workspace (foundational setup experience)
blackwell init workspace

# Interactive quickstart guide
blackwell quickstart

# Initialize with specific configuration
blackwell init workspace --platform-path ../platform-infrastructure
```

### 🏗️ **Understanding Workspace Initialization**

The `blackwell init workspace` command is the **foundational setup experience** that transforms Blackwell CLI from a basic tool into an intelligent development environment. This single command orchestrates a comprehensive configuration process that enables all advanced features.

#### **🎯 What is Workspace Initialization?**

Workspace initialization is the cornerstone of the Blackwell CLI experience. It creates a complete, personalized development environment by:

- **Creating Configuration Infrastructure**: Establishes `~/.blackwell/config.yml` with intelligent defaults
- **Enabling Platform Integration**: Discovers and connects to platform-infrastructure for live metadata
- **Configuring AWS Integration**: Sets up AWS profiles and region preferences for deployment
- **Establishing Default Preferences**: Configures your preferred providers and service tiers
- **Validating System Dependencies**: Ensures all required tools and permissions are available

#### **🔄 The Foundational Setup Experience**

```bash
# Run the foundational setup
blackwell init workspace

# Interactive prompts you'll see:
# 🏗️  Blackwell CLI Workspace Initialization
#
# ❓ AWS Profile (leave blank for default): blackwellsystems
# ❓ Preferred AWS Region: us-west-2
# ❓ Default CMS Provider (decap/tina/sanity/contentful): decap
# ❓ Default E-commerce Provider (snipcart/foxy/shopify_basic): snipcart
# ❓ Default SSG Engine (hugo/eleventy/astro/gatsby/nextjs/nuxt): astro
# ❓ Service Tier Preference (tier1/tier2/tier3): tier1
# ❓ Auto-discover platform-infrastructure? [Y/n]: Y
#
# 🔍 Discovering platform-infrastructure...
# ✅ Found platform-infrastructure at ../platform-infrastructure
# ✅ Platform integration enabled - dynamic mode activated
# ✅ Configuration saved to ~/.blackwell/config.yml
# ✅ AWS credentials validated
# ✅ System dependencies verified
#
# 🎉 Workspace initialized successfully!
# Your CLI now has access to 15+ stack types and intelligent recommendations.
```

#### **🚀 System Transformation Benefits**

**Before Workspace Initialization:**
```bash
# Limited functionality - static mode only
blackwell create client  # ❌ Basic provider set, no intelligence
blackwell cost estimate  # ❌ Static cost rules only
blackwell platform status  # ❌ "Not configured"
```

**After Workspace Initialization:**
```bash
# Full intelligent capabilities - dynamic mode
blackwell create client  # ✅ 15+ providers, smart recommendations
blackwell cost estimate  # ✅ Real-time accurate costs from platform
blackwell platform status  # ✅ Live integration status, metadata count
blackwell platform providers  # ✅ Dynamic provider discovery
```

#### **🎛️ Configuration Components Created**

The workspace initialization creates a comprehensive configuration structure:

```yaml
# ~/.blackwell/config.yml (created by workspace init)
version: "0.1.0"

# Your personalized AWS setup
aws:
  profile: "blackwellsystems"     # From your input
  region: "us-west-2"             # From your input
  account_id: "123456789012"      # Auto-detected

# Your preferred defaults
defaults:
  cms_provider: "decap"           # From your input
  ecommerce_provider: "snipcart"  # From your input
  ssg_engine: "astro"             # From your input
  service_tier: "tier1"           # From your input
  integration_mode: "event_driven"

# Platform integration (auto-configured)
platform_infrastructure:
  path: "../platform-infrastructure"  # Auto-discovered
  auto_discover: true
  force_static_mode: false             # Dynamic mode enabled
  enable_live_metadata: true           # Intelligence enabled
  cache_duration: 300
```

#### **💡 Why Workspace Initialization is Essential**

1. **Enables Intelligence**: Without workspace init, CLI operates in limited static mode
2. **Personalizes Experience**: Your preferences become the smart defaults for all operations
3. **Activates Platform Integration**: Connects to live metadata for accurate recommendations
4. **Validates Environment**: Ensures AWS credentials, dependencies, and permissions work
5. **Creates Foundation**: Every other CLI command builds upon this configuration foundation

#### **🔧 Advanced Initialization Options**

```bash
# Non-interactive mode (use defaults)
blackwell init workspace --non-interactive

# Force reinitialize existing workspace
blackwell init workspace --force

# Skip platform integration discovery
blackwell init workspace --no-platform-discovery

# Set specific platform path during init
blackwell init workspace --platform-path /custom/path/to/platform
```

### 🏗️ **Client Creation**

```bash
# Create new client (interactive)
blackwell create client

# Create with specific providers
blackwell create client \
  --client-id "my-startup" \
  --cms-provider decap \
  --ecommerce-provider snipcart \
  --ssg-engine hugo

# Create from template
blackwell create client --template budget-startup
```

### 🚀 **Deployment Management**

```bash
# Deploy client infrastructure (includes automatic bootstrap validation)
blackwell deploy client my-startup --profile blackwellsystems

# Deploy with specific AWS parameters
blackwell deploy client my-startup \
  --profile blackwellsystems \
  --account 105249142972 \
  --region us-west-2 \
  --approve

# Preview deployment without executing (dry-run)
blackwell deploy client my-startup --dry-run

# Deploy shared infrastructure (foundational resources)
blackwell deploy shared --profile blackwellsystems --approve

# Check deployment status
blackwell deploy status --profile blackwellsystems

# Destroy infrastructure (with safety prompts)
blackwell deploy destroy my-startup --profile blackwellsystems

# Force destroy (skip confirmations - use with caution)
blackwell deploy destroy my-startup --profile blackwellsystems --force
```

**Deployment Process with Bootstrap Integration:**
1. **Pre-flight Validation**: Checks AWS credentials, CDK availability
2. **Bootstrap Verification**: Validates CDK bootstrap status
3. **Configuration Validation**: Ensures client configuration is valid
4. **Infrastructure Synthesis**: Generates CDK deployment scripts
5. **Deployment Execution**: Applies infrastructure changes
6. **Post-deployment Validation**: Confirms successful deployment

**Bootstrap Integration Features:**
- **Automatic Detection**: All deploy commands check bootstrap status
- **Interactive Guidance**: Prompts to bootstrap if missing
- **Safety Checks**: Prevents deployments to unbootstrapped accounts
- **Skip Option**: `--skip-bootstrap-check` to bypass validation

### 💰 **Cost Management**

```bash
# Estimate costs for configuration
blackwell cost estimate \
  --cms-provider sanity \
  --ecommerce-provider snipcart \
  --ssg-engine astro

# Compare provider costs
blackwell cost compare

# Show cost breakdown
blackwell cost breakdown --client-id my-startup
```

### 📋 **Information Commands**

```bash
# List all clients
blackwell list clients

# List available providers
blackwell list providers

# List deployments
blackwell list deployments

# Show client details
blackwell list client --client-id my-startup
```

### 🗑️ **Deletion Commands**

```bash
# Delete client configuration (with safety checks)
blackwell delete client my-startup

# Delete client configuration (skip confirmation)
blackwell delete client my-startup --force

# Delete client config but preserve AWS deployments
blackwell delete client my-startup --preserve-deployments

# Delete template
blackwell delete template my-template

# Delete template (skip confirmation)
blackwell delete template my-template --force
```

**⚠️ Important Safety Notes:**
- Client deletion only removes **local configuration** by default
- AWS resources remain active unless explicitly destroyed first
- Always run `blackwell deploy destroy <client>` before deletion to clean up AWS resources
- Use `--preserve-deployments` to keep AWS resources and only delete local config

### 🔧 **Migration & Updates**

```bash
# Migrate between providers
blackwell migrate \
  --client-id my-startup \
  --from-cms decap \
  --to-cms sanity

# Upgrade provider versions
blackwell migrate upgrade --client-id my-startup

# Switch integration modes
blackwell migrate integration-mode \
  --client-id my-startup \
  --mode event-driven
```

---

## CDK Bootstrap Management

AWS CDK requires bootstrapping to deploy infrastructure. The Blackwell CLI provides comprehensive bootstrap detection, validation, and management across multiple AWS accounts and regions.

### 🏗️ **What is CDK Bootstrap?**

CDK Bootstrap creates essential AWS resources for CDK deployments:
- **CDKToolkit CloudFormation Stack**: Core infrastructure management
- **S3 Assets Bucket**: Storage for deployment artifacts
- **ECR Repository**: Container image storage (when needed)
- **IAM Execution Roles**: Permissions for deployments

`★ Insight ─────────────────────────────────────`
Bootstrap is **one-time per account/region** but critical for all deployments. The CLI automatically detects bootstrap status and provides intelligent guidance for missing resources.
`─────────────────────────────────────────────────`

### 📊 **Bootstrap Status Checking**

```bash
# Check bootstrap status for current account/region
blackwell deploy bootstrap status

# Check with specific AWS profile
blackwell deploy bootstrap status --profile blackwellsystems

# Detailed resource validation
blackwell deploy bootstrap status --verbose

# Check specific account/region
blackwell deploy bootstrap status \
  --profile blackwellsystems \
  --account 105249142972 \
  --region us-west-2 \
  --verbose
```

**Expected Output:**
```
CDK Bootstrap Status - 105249142972/us-west-2
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property         ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Account ID       │ 105249142972            │
│ Region           │ us-west-2               │
│ Profile          │ blackwellsystems        │
│ Bootstrap Status │ ✓ Bootstrapped          │
│ CDKToolkit Stack │ ✓ Exists                │
│ Checked At       │ 2025-10-11 20:15:13 UTC │
└──────────────────┴─────────────────────────┘

                Bootstrap Resource Details
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Resource                  ┃ Type      ┃ Status    ┃ ARN/Details              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ cdk-hnb659fds-assets-... │ S3 Bucket │ ✓ Healthy │ arn:aws:s3:::cdk-hnb659… │
│ cdk-hnb659fds-cfn-exec-r │ Iam Roles │ ✓ Healthy │ arn:aws:iam::105249142...│
│ cdk-hnb659fds-deploy-role│ Iam Roles │ ✓ Healthy │ arn:aws:iam::105249142...│
│ cdk-hnb659fds-file-publ..│ Iam Roles │ ✓ Healthy │ arn:aws:iam::105249142...│
│ cdk-hnb659fds-image-publ.│ Iam Roles │ ✓ Healthy │ arn:aws:iam::105249142...│
└───────────────────────────┴───────────┴───────────┴──────────────────────────┘
```

### 🚀 **Running Bootstrap**

```bash
# Bootstrap current account/region
blackwell deploy bootstrap run

# Bootstrap with specific profile and approve automatically
blackwell deploy bootstrap run --profile blackwellsystems --approve

# Bootstrap specific account/region
blackwell deploy bootstrap run \
  --profile blackwellsystems \
  --account 105249142972 \
  --region us-west-2 \
  --approve

# Force bootstrap (even if already bootstrapped)
blackwell deploy bootstrap run --force --approve

# Preview what would be bootstrapped (dry-run)
blackwell deploy bootstrap run --dry-run
```

**Bootstrap Process:**
1. **Pre-flight Checks**: Validates AWS credentials and CDK availability
2. **Current Status**: Checks existing bootstrap state
3. **Confirmation**: Interactive approval (unless `--approve` used)
4. **Execution**: Runs `cdk bootstrap` with proper account/region context
5. **Verification**: Validates successful bootstrap completion

### 🔍 **Bootstrap Validation**

```bash
# Comprehensive bootstrap validation
blackwell deploy bootstrap validate --profile blackwellsystems

# Attempt automatic fixes for issues
blackwell deploy bootstrap validate --profile blackwellsystems --fix

# Validate specific account/region
blackwell deploy bootstrap validate \
  --profile blackwellsystems \
  --account 105249142972 \
  --region us-west-2
```

**Validation Checks:**
- **CDKToolkit Stack**: CloudFormation stack existence and health
- **S3 Assets Bucket**: Bucket availability and permissions
- **ECR Repository**: Container registry (if needed)
- **IAM Execution Roles**: All 4 required roles and permissions
- **Resource Consistency**: Cross-resource validation

### 🌍 **Multi-Region Bootstrap Management**

```bash
# Check bootstrap status across multiple regions
blackwell deploy bootstrap regions \
  --profile blackwellsystems \
  --include us-west-2,us-east-1,eu-west-1

# Check all common regions (default behavior)
blackwell deploy bootstrap regions --profile blackwellsystems

# Exclude specific regions
blackwell deploy bootstrap regions \
  --profile blackwellsystems \
  --exclude ap-southeast-1,ap-northeast-1

# Bootstrap all missing regions automatically
blackwell deploy bootstrap regions \
  --profile blackwellsystems \
  --include us-west-2,us-east-1 \
  --bootstrap-missing

# Preview multi-region bootstrap (dry-run)
blackwell deploy bootstrap regions \
  --profile blackwellsystems \
  --bootstrap-missing \
  --dry-run
```

**Multi-Region Output:**
```
                 CDK Bootstrap Status Summary
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Region    ┃ Bootstrap Status ┃ CDKToolkit Stack ┃ Resources ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ us-west-2 │ ✓ Ready          │ ✓                │ 5/5       │
│ us-east-1 │ ⚠ Partial        │ ✓                │ 1/5       │
│ eu-west-1 │ ✗ Missing        │ ✗                │ 0/0       │
└───────────┴──────────────────┴──────────────────┴───────────┘
```

### 🛡️ **Bootstrap Safety Features**

**Interactive Confirmations:**
- Account/region validation before bootstrap
- Resource impact warnings
- Cost implications (minimal for bootstrap)

**Comprehensive Error Handling:**
- AWS credential validation
- CDK installation verification
- Network connectivity checks
- Graceful failure recovery

**Multi-Profile Support:**
- Per-profile bootstrap management
- Cross-account bootstrap coordination
- Profile-specific credential handling

---

## System Diagnostics

The Blackwell CLI provides comprehensive system diagnostics to ensure optimal deployment readiness and troubleshoot issues across all components.

### 🏥 **Comprehensive System Doctor**

```bash
# Complete system diagnostics
blackwell doctor

# Verbose diagnostics with detailed information
blackwell doctor --verbose

# Deployment-specific readiness check
blackwell doctor --deployment-check

# Deployment readiness for specific account
blackwell doctor --deployment-check \
  --profile blackwellsystems \
  --account 105249142972 \
  --region us-west-2
```

**System Doctor Checks:**
1. **System Dependencies**: Python, Node.js, AWS CDK, AWS CLI, Git
2. **AWS Configuration**: Credentials, regions, profiles
3. **CDK Bootstrap Status**: Account/region bootstrap validation
4. **Platform Integration**: Dynamic provider matrix status
5. **Configuration Health**: CLI configuration validation

**Expected Output:**
```
                                   ✓ Healthy
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check                ┃ Status                    ┃ Details                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python Version       │ Python 3.13.3            │ Blackwell CLI requires    │
│                      │ (compatible)              │ Python 3.13+              │
│ AWS CDK              │ CDK 2.1029.4              │ AWS Cloud Development Kit │
│                      │ (available)               │                           │
│ AWS Credentials      │ AWS credentials are       │ Account: 105249142972     │
│                      │ configured and valid      │ Identity: user@domain.com │
│ CDK Bootstrap        │ Account 105249142972      │ CDK version: detected     │
│                      │ region us-west-2 is      │                           │
│                      │ bootstrapped              │                           │
│ Platform Integration │ Platform integration is   │ Dynamic provider matrix   │
│                      │ active                    │ available                 │
└──────────────────────┴───────────────────────────┴───────────────────────────┘

✅ System Health: Good - All critical checks passed!
```

### 🔧 **Deployment Readiness Check**

```bash
# Quick deployment readiness validation
blackwell doctor --deployment-check --profile blackwellsystems

# Expected output for ready system:
# ✅ System is ready for deployment!
# Target: 105249142972/us-west-2

# Expected output for issues:
# ❌ System is not ready for deployment
# Issues to resolve:
#   • CDK is not bootstrapped in 105249142972/us-west-2
# 💡 Quick fixes:
#    blackwell deploy bootstrap
```

### 🏗️ **Platform-Specific Diagnostics**

```bash
# Platform integration diagnostics
blackwell platform doctor

# Extended platform diagnostics
blackwell platform status --verbose
```

**Platform Doctor Features:**
- **Integration Status**: Platform-infrastructure connection
- **Provider Matrix Test**: Dynamic provider loading
- **Configuration Validation**: Settings and paths
- **CDK Bootstrap Status**: Infrastructure readiness
- **Recommendations**: Optimization suggestions

---

## Provider Management

### 🔍 **Provider Discovery**

The CLI automatically discovers providers from platform-infrastructure when available, with intelligent fallback to static definitions.

```bash
# Show all available providers with sources
blackwell platform providers

# Expected output shows dynamic data:
# Data source: platform
#
# CMS Providers
# ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Provider   ┃ Name               ┃ Features                            ┃
# ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
# │ decap      │ Decap CMS          │ Git-based, Free, Version control   │
# │ tina       │ TinaCMS            │ Visual editing, Git workflow       │
# │ sanity     │ Sanity Studio      │ Structured content, Real-time      │
# │ contentful │ Contentful         │ Enterprise CMS, Advanced workflow  │
# └────────────┴────────────────────┴─────────────────────────────────────┘
```

### ⚡ **Dynamic vs Static Comparison**

| Feature | Dynamic Mode | Static Mode |
|---------|-------------|-------------|
| **Data Source** | Live platform-infrastructure | Built-in definitions |
| **Provider Count** | 15+ stack types | Basic provider set |
| **Cost Estimation** | Accurate, real-time | Static estimates |
| **Recommendations** | Intelligent, contextual | Rule-based |
| **Updates** | Automatic synchronization | Manual CLI updates |
| **Reliability** | High (with fallback) | Maximum |
| **Features** | Enhanced intelligence | Core functionality |

### 🎯 **Smart Provider Selection**

```bash
# Get intelligent recommendations
blackwell create client --interactive

# The CLI will ask questions and provide smart suggestions:
# "Based on your requirements (budget-conscious, technical team),
#  we recommend: Decap CMS + Snipcart + Hugo for optimal cost/performance"
```

---

## Configuration System

### 📁 **Configuration Hierarchy**

1. **Environment Variables** (highest priority)
2. **Configuration File** (`~/.blackwell/config.yml`)
3. **CLI Arguments** (command-specific)
4. **Default Values** (lowest priority)

### 🌍 **Environment Variables**

```bash
# Platform integration control
export BLACKWELL_FORCE_STATIC=true          # Force static mode
export BLACKWELL_PLATFORM_PATH=/path/to/platform
export BLACKWELL_ENABLE_LIVE_METADATA=false

# AWS configuration
export BLACKWELL_AWS_PROFILE=my-profile
export BLACKWELL_AWS_REGION=us-west-2

# CLI behavior
export BLACKWELL_VERBOSE=true
```

### ⚙️ **Configuration Commands**

```bash
# Show current configuration
blackwell config show

# Show specific section
blackwell config show --section platform_infrastructure

# Set configuration values
blackwell config set platform_infrastructure.force_static_mode false
blackwell config set aws.profile my-profile
blackwell config set defaults.cms_provider sanity

# Remove configuration values
blackwell config unset platform_infrastructure.cache_duration

# Reset to defaults
blackwell config reset

# Show configuration file path
blackwell config path
```

### 📋 **Configuration Structure**

```yaml
# ~/.blackwell/config.yml
version: "0.1.0"

# AWS Configuration
aws:
  profile: "blackwellsystems"
  region: "us-west-2"
  account_id: null  # Auto-detected

# Default Settings
defaults:
  cms_provider: "decap"
  ecommerce_provider: "snipcart"
  ssg_engine: "astro"
  integration_mode: "event_driven"
  service_tier: "tier1"
  management_model: "self_managed"

# Platform Integration
platform_infrastructure:
  path: "../platform-infrastructure"
  auto_discover: true
  required_version: "1.0.0"
  force_static_mode: false
  enable_live_metadata: true
  cache_duration: 300  # seconds

# CLI Behavior
verbose: false
auto_confirm: false
check_updates: true
telemetry: true
```

---

## Real-World Workflows

### 🏃‍♂️ **Quick Start: Budget Startup**

```bash
# 1. Initialize with platform integration
blackwell init workspace
blackwell platform path --auto-discover
blackwell platform enable

# 2. Verify system readiness (including CDK bootstrap)
blackwell doctor --deployment-check --profile blackwellsystems
# If bootstrap needed: blackwell deploy bootstrap run --profile blackwellsystems --approve

# 3. Create budget-friendly client
blackwell create client \
  --client-id "budget-startup" \
  --cms-provider decap \
  --ecommerce-provider snipcart \
  --ssg-engine hugo \
  --interactive

# 4. Review cost estimate
blackwell cost estimate --client-id budget-startup
# Expected: $8-15/month total cost

# 5. Deploy infrastructure (with automatic bootstrap validation)
blackwell deploy --client-id budget-startup

# 6. Monitor and manage
blackwell list deployments
blackwell platform refresh  # Keep metadata current
```

### 🏢 **Enterprise Workflow**

```bash
# 1. Set up enterprise configuration
blackwell config set defaults.service_tier tier3
blackwell config set defaults.cms_provider contentful
blackwell config set defaults.ecommerce_provider shopify_basic

# 2. Comprehensive system validation
blackwell doctor --verbose
blackwell platform status

# 3. Multi-region bootstrap preparation (enterprise typically uses multiple regions)
blackwell deploy bootstrap regions \
  --profile blackwellsystems \
  --include us-west-2,us-east-1,eu-west-1 \
  --bootstrap-missing

# 4. Create enterprise client with composition
blackwell create client \
  --client-id "enterprise-corp" \
  --cms-provider contentful \
  --ecommerce-provider shopify_basic \
  --ssg-engine gatsby \
  --integration-mode event-driven

# 5. Deployment readiness check
blackwell doctor --deployment-check --profile blackwellsystems

# 6. Deploy with monitoring
blackwell deploy --client-id enterprise-corp --verbose

# 7. Ongoing management
blackwell cost breakdown --client-id enterprise-corp
blackwell migrate upgrade --client-id enterprise-corp
```

### 🔄 **Provider Migration Workflow**

```bash
# 1. Assess current setup
blackwell list client --client-id my-client
blackwell cost estimate --client-id my-client

# 2. Plan migration
blackwell migrate plan \
  --client-id my-client \
  --from-cms decap \
  --to-cms sanity

# 3. Execute migration
blackwell migrate execute \
  --client-id my-client \
  --migration-plan migration-plan.json

# 4. Verify and optimize
blackwell deploy --client-id my-client --dry-run
blackwell cost compare --before migration-before.json
```

---

## Advanced Features

### 🧠 **Intelligent Recommendations**

```bash
# Get contextual recommendations based on requirements
blackwell create client --interactive

# Sample interaction:
# ❓ What's your budget range? (budget/professional/enterprise)
# ❓ Do you need e-commerce? (yes/no)
# ❓ Team technical expertise? (beginner/intermediate/advanced)
# ❓ Content complexity? (simple/structured/enterprise)
#
# 💡 Based on your answers, we recommend:
#    CMS: Tina (visual editing for mixed-skill teams)
#    E-commerce: Snipcart (cost-effective, simple integration)
#    SSG: Astro (modern performance, component flexibility)
#    Mode: Event-driven (future composition flexibility)
```

### 🔍 **Advanced Provider Analysis**

```bash
# Detailed compatibility checking
blackwell analyze compatibility \
  --cms-provider sanity \
  --ecommerce-provider snipcart \
  --ssg-engine astro

# Performance benchmarking
blackwell analyze performance \
  --ssg-engine hugo \
  --compare-with eleventy,astro

# Cost optimization suggestions
blackwell cost optimize --client-id my-client
```

### 🎛️ **Multi-Environment Management**

```bash
# Environment-specific configurations
blackwell config set --env dev defaults.service_tier tier1
blackwell config set --env prod defaults.service_tier tier2

# Deploy to specific environments
blackwell deploy --client-id my-client --env dev
blackwell deploy --client-id my-client --env prod

# Environment comparison
blackwell compare environments --client-id my-client
```

### 📊 **Analytics & Monitoring**

```bash
# Deployment analytics
blackwell analytics deployments --timeframe 30d

# Cost tracking
blackwell analytics costs --client-id my-client --monthly

# Platform integration health
blackwell analytics platform-health

# Usage patterns
blackwell analytics usage --breakdown provider
```

---

## Troubleshooting

### 🚨 **Common Issues & Solutions**

#### **Platform Integration Not Working**

```bash
# Symptoms: "Platform Availability: ✗ Unavailable"

# Diagnosis:
blackwell platform doctor

# Solutions:
# 1. Check platform path
blackwell platform path --auto-discover

# 2. Verify platform installation
cd ../platform-infrastructure && uv sync

# 3. Add as dependency
uv add --editable ../platform-infrastructure

# 4. Test direct import
uv run python -c "from shared.factories.platform_stack_factory import PlatformStackFactory; print('✅ Success')"
```

#### **Missing Dependencies**

```bash
# Symptoms: "ModuleNotFoundError: No module named 'pydantic'"

# Solutions:
# 1. Install with uv (recommended)
uv sync

# 2. Or install missing packages individually
uv add pydantic typer rich

# 3. Verify installation
uv run blackwell --version
```

#### **Configuration Issues**

```bash
# Symptoms: Various configuration-related errors

# Diagnosis:
blackwell config show
blackwell doctor

# Solutions:
# 1. Reset configuration
blackwell config reset

# 2. Check file permissions
ls -la ~/.blackwell/config.yml

# 3. Validate configuration
blackwell doctor
```

#### **AWS Integration Problems**

```bash
# Symptoms: AWS credential or permission errors

# Diagnosis:
blackwell doctor
aws sts get-caller-identity

# Solutions:
# 1. Configure AWS profile
aws configure --profile blackwellsystems

# 2. Set profile in CLI
blackwell config set aws.profile blackwellsystems

# 3. Verify permissions
aws iam get-user
```

#### **CDK Bootstrap Issues**

```bash
# Symptoms: "CDK is not bootstrapped" or deployment failures

# Diagnosis:
blackwell deploy bootstrap status --profile blackwellsystems --verbose
blackwell doctor --deployment-check --profile blackwellsystems

# Solutions:
# 1. Bootstrap the account/region
blackwell deploy bootstrap run --profile blackwellsystems --approve

# 2. Force bootstrap (if partial bootstrap exists)
blackwell deploy bootstrap run --profile blackwellsystems --force --approve

# 3. Validate bootstrap completion
blackwell deploy bootstrap validate --profile blackwellsystems

# 4. Multi-region bootstrap (if needed)
blackwell deploy bootstrap regions --profile blackwellsystems --bootstrap-missing

# Common bootstrap error fixes:
# - Missing CDK installation: npm install -g aws-cdk
# - Insufficient permissions: Ensure AdministratorAccess or equivalent
# - Network issues: Check connectivity to AWS services
# - Partial bootstrap: Use --force flag to complete
```

#### **Deployment Readiness Problems**

```bash
# Symptoms: Deployment fails with infrastructure errors

# Comprehensive diagnosis:
blackwell doctor --verbose
blackwell deploy bootstrap status --profile blackwellsystems --verbose
blackwell platform doctor

# Step-by-step resolution:
# 1. Check system dependencies
blackwell doctor

# 2. Validate AWS configuration
aws sts get-caller-identity --profile blackwellsystems

# 3. Ensure CDK bootstrap
blackwell deploy bootstrap run --profile blackwellsystems --approve

# 4. Verify platform integration
blackwell platform status

# 5. Test deployment readiness
blackwell doctor --deployment-check --profile blackwellsystems
```

### 🔧 **Emergency Recovery**

```bash
# Force static mode (emergency operation)
export BLACKWELL_FORCE_STATIC=true
blackwell platform disable

# Reset all configuration
blackwell config reset
rm -rf ~/.blackwell/

# CDK bootstrap recovery (if deployments are failing)
# 1. Check current bootstrap state
blackwell deploy bootstrap status --profile blackwellsystems --verbose

# 2. Force re-bootstrap (nuclear option)
blackwell deploy bootstrap run --profile blackwellsystems --force --approve

# 3. Multi-region recovery (if using multiple regions)
blackwell deploy bootstrap regions \
  --profile blackwellsystems \
  --include us-west-2,us-east-1 \
  --bootstrap-missing

# Complete system recovery
blackwell doctor --verbose
blackwell init workspace
```

### 📞 **Getting Help**

```bash
# Built-in help system
blackwell --help
blackwell platform --help
blackwell create client --help

# System diagnostics
blackwell doctor

# Verbose operation for debugging
blackwell --verbose platform status

# Configuration validation
blackwell config show
```

---

## Migration from Static Mode

### 🔄 **Upgrading from Static CLI**

If you've been using Blackwell CLI in static mode, here's how to enable the new platform integration:

#### **Step 1: Backup Current Setup**

```bash
# Backup existing configuration
cp ~/.blackwell/config.yml ~/.blackwell/config.yml.backup

# Export current client list
blackwell list clients --format json > clients-backup.json
```

#### **Step 2: Install Platform Integration**

```bash
# Add platform-infrastructure dependency
cd blackwell-cli
uv add --editable ../platform-infrastructure

# Verify platform availability
blackwell platform status
```

#### **Step 3: Enable Dynamic Mode**

```bash
# Set platform path
blackwell platform path --set ../platform-infrastructure

# Enable integration
blackwell platform enable

# Verify enhanced functionality
blackwell platform providers
```

#### **Step 4: Test Enhanced Features**

```bash
# Test intelligent recommendations (new feature)
blackwell create client --interactive

# Test enhanced cost estimation (improved accuracy)
blackwell cost estimate --cms-provider sanity --ecommerce-provider snipcart

# Test metadata refresh (new capability)
blackwell platform refresh
```

#### **Step 5: Optimize Configuration**

```bash
# Update defaults to use enhanced features
blackwell config set defaults.integration_mode event_driven
blackwell config set platform_infrastructure.enable_live_metadata true

# Verify optimized setup
blackwell doctor
```

### 📈 **Benefits After Migration**

| Feature | Before (Static) | After (Dynamic) |
|---------|----------------|-----------------|
| **Provider Data** | Hardcoded in CLI | Live from platform |
| **Stack Types** | Basic set | 15+ with metadata |
| **Cost Estimation** | Static rules | Real-time accuracy |
| **Recommendations** | Basic logic | AI-driven intelligence |
| **Updates** | Manual CLI updates | Automatic sync |
| **New Features** | CLI release cycle | Platform updates |

---

## 🎉 **Conclusion**

Blackwell CLI with platform integration represents a quantum leap in web development tooling. By combining **intelligent provider selection**, **live platform data**, and **resilient architecture**, it delivers enterprise-grade capabilities with startup-friendly simplicity.

### **Key Achievements:**

✅ **Zero-Risk Integration** - Safe import patterns ensure reliability
✅ **Enhanced Intelligence** - Live metadata enables smart recommendations
✅ **Complete Control** - Multiple layers of configuration and control
✅ **Future-Proof** - Automatic synchronization with platform evolution
✅ **Production Ready** - Comprehensive diagnostics and error handling
✅ **Enterprise AWS Integration** - Complete CDK bootstrap management and multi-region support
✅ **Deployment Intelligence** - Automatic infrastructure readiness validation

### **Ready to Get Started?**

```bash
# Quick start
blackwell init workspace
blackwell platform path --auto-discover
blackwell platform enable
blackwell quickstart

# You're now ready to build with the future of web development! 🚀
```

---

*📚 This guide covers Blackwell CLI v0.1.0 with Platform Integration. For updates and advanced topics, check the project repository and documentation.*