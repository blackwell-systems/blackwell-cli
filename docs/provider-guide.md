# Provider Selection Guide

A comprehensive guide to choosing the right CMS, e-commerce, and SSG providers for your project needs and budget.

## Table of Contents

- [Overview](#overview)
- [CMS Providers](#cms-providers)
- [E-commerce Providers](#ecommerce-providers)
- [SSG Engines](#ssg-engines)
- [Provider Combinations](#provider-combinations)
- [Selection Framework](#selection-framework)
- [Compatibility Matrix](#compatibility-matrix)

## Overview

The Blackwell CLI supports **21+ provider combinations** across different categories:

- **4 CMS Providers**: Decap, Tina, Sanity, Contentful
- **3 E-commerce Providers**: Snipcart, Foxy.io, Shopify Basic
- **6 SSG Engines**: Hugo, Eleventy, Astro, Gatsby, Next.js, Nuxt.js

### Key Benefits of Provider Flexibility

- 🔓 **No Vendor Lock-in**: Switch providers without infrastructure changes
- 💰 **Cost Optimization**: Choose based on features needed, not full suite pricing
- 🎯 **Best-of-Breed**: Mix specialized providers for optimal results
- 🚀 **Future-Proof**: Easy migration paths as needs change

## CMS Providers

### Decap CMS (Formerly Netlify CMS)

**💰 Cost**: **FREE**
**⚡ Complexity**: Low
**🎯 Best For**: Budget-conscious teams, technical users, simple content needs

#### Pros
- ✅ **Completely free** - no monthly costs
- ✅ **Git-based workflow** - version control for content
- ✅ **Simple setup** - minimal configuration required
- ✅ **No vendor dependencies** - self-hosted admin interface
- ✅ **Markdown support** - developer-friendly content format

#### Cons
- ❌ **Technical users only** - requires Git knowledge
- ❌ **Limited collaboration** - no real-time editing
- ❌ **Basic media management** - no advanced asset handling
- ❌ **No content scheduling** - publish immediately only

#### Ideal Use Cases
- Personal blogs and portfolios
- Developer documentation sites
- Small business websites with technical teams
- Prototypes and MVPs with tight budgets

#### Example Configuration
```bash
blackwell init project tech-blog \
  --cms decap \
  --ssg hugo \
  --integration direct \
  --budget 50
```

---

### Tina CMS

**💰 Cost**: **$0-99/month** (Free tier: 2 users, Starter: $29/month)
**⚡ Complexity**: Medium
**🎯 Best For**: Visual editing needs, small to medium teams

#### Pros
- ✅ **Visual editing** - inline content editing
- ✅ **Git-based** - version control with user-friendly interface
- ✅ **Real-time collaboration** - multiple editors
- ✅ **Developer-friendly** - TypeScript configuration
- ✅ **Free tier available** - good for small projects

#### Cons
- ❌ **Limited free tier** - only 2 users
- ❌ **React ecosystem focus** - works best with React-based SSGs
- ❌ **Newer platform** - smaller community and ecosystem
- ❌ **Configuration complexity** - requires technical setup

#### Ideal Use Cases
- Small creative agencies
- Marketing websites with non-technical content editors
- React-based applications
- Teams needing visual editing on a budget

#### Example Configuration
```bash
blackwell init project creative-agency \
  --cms tina \
  --ssg astro \
  --integration event_driven \
  --budget 120
```

---

### Sanity CMS

**💰 Cost**: **$0-199/month** (Free: 3 users, Team: $99/month)
**⚡ Complexity**: Medium-High
**🎯 Best For**: Structured content, growing businesses, flexible content modeling

#### Pros
- ✅ **Structured content** - powerful schema and relationships
- ✅ **Real-time collaboration** - multi-user editing
- ✅ **Flexible content modeling** - custom content types
- ✅ **Great developer experience** - excellent APIs and tooling
- ✅ **Scalable free tier** - generous usage limits

#### Cons
- ❌ **Learning curve** - requires understanding of structured content
- ❌ **Configuration complexity** - schema setup required
- ❌ **API-dependent** - requires internet for editing
- ❌ **Pricing jumps** - significant cost increase at scale

#### Ideal Use Cases
- E-commerce sites with complex product catalogs
- Multi-site content management
- Applications requiring structured data
- Teams with content modeling needs

#### Example Configuration
```bash
blackwell init project ecommerce-site \
  --cms sanity \
  --ecommerce snipcart \
  --ssg astro \
  --integration event_driven \
  --budget 180
```

---

### Contentful

**💰 Cost**: **$300-1000+/month** (Team: $300/month)
**⚡ Complexity**: High
**🎯 Best For**: Enterprise teams, complex workflows, large-scale content operations

#### Pros
- ✅ **Enterprise features** - advanced permissions, workflows
- ✅ **Mature platform** - established ecosystem and integrations
- ✅ **Advanced collaboration** - approval workflows, content scheduling
- ✅ **Powerful APIs** - GraphQL and REST with excellent performance
- ✅ **Multi-language support** - built-in internationalization

#### Cons
- ❌ **Expensive** - high monthly costs
- ❌ **Complex setup** - requires significant configuration
- ❌ **Vendor lock-in risk** - proprietary content models
- ❌ **Overkill for simple sites** - many unused features

#### Ideal Use Cases
- Large enterprise websites
- Multi-brand content management
- Complex approval workflows
- International content operations

#### Example Configuration
```bash
blackwell init project enterprise-corp \
  --cms contentful \
  --ecommerce shopify_basic \
  --ssg gatsby \
  --integration event_driven \
  --budget 500
```

## E-commerce Providers

### Snipcart

**💰 Cost**: **$29/month + 2% transaction fees** (Free up to $500 in sales)
**⚡ Complexity**: Low
**🎯 Best For**: Simple stores, digital products, budget-conscious businesses

#### Pros
- ✅ **Simple integration** - add to any static site
- ✅ **Low barrier to entry** - free tier available
- ✅ **Developer-friendly** - HTML data attributes
- ✅ **No inventory management** - product data in your CMS
- ✅ **Subscription support** - recurring billing built-in

#### Cons
- ❌ **Limited customization** - fewer advanced features
- ❌ **Transaction fees** - 2% on all sales
- ❌ **Basic reporting** - limited analytics
- ❌ **Customer management** - minimal CRM features

#### Ideal Use Cases
- Digital product sales
- Simple physical product stores
- Subscription services
- Sites where products are managed in CMS

#### Example Configuration
```bash
blackwell init project digital-store \
  --cms sanity \
  --ecommerce snipcart \
  --ssg astro \
  --integration event_driven
```

---

### Foxy.io

**💰 Cost**: **$75-300/month + 1.5% transaction fees**
**⚡ Complexity**: Medium-High
**🎯 Best For**: Advanced customization, complex business models, subscription businesses

#### Pros
- ✅ **Lower transaction fees** - 1.5% vs competitors' 2%+
- ✅ **Highly customizable** - extensive templating system
- ✅ **Advanced features** - complex pricing, subscriptions
- ✅ **Better for high volume** - scales well with sales
- ✅ **Flexible checkout** - custom checkout flows

#### Cons
- ❌ **Higher base cost** - $75+ monthly minimum
- ❌ **Complex setup** - requires more technical knowledge
- ❌ **Smaller ecosystem** - fewer integrations than Shopify
- ❌ **Learning curve** - advanced features require time investment

#### Ideal Use Cases
- High-volume e-commerce ($50K+ monthly sales)
- Complex subscription models
- Custom checkout requirements
- Businesses needing advanced pricing rules

#### Example Configuration
```bash
blackwell init project subscription-biz \
  --cms sanity \
  --ecommerce foxy \
  --ssg astro \
  --integration event_driven \
  --budget 250
```

---

### Shopify Basic

**💰 Cost**: **$29/month + 2.9% transaction fees**
**⚡ Complexity**: Medium
**🎯 Best For**: Traditional e-commerce, proven reliability, full-featured stores

#### Pros
- ✅ **Proven platform** - established and reliable
- ✅ **Full e-commerce features** - inventory, orders, customers
- ✅ **Large ecosystem** - thousands of apps and themes
- ✅ **Built-in marketing** - SEO, email, social media tools
- ✅ **Mobile commerce** - excellent mobile experience

#### Cons
- ❌ **Higher transaction fees** - 2.9% standard rate
- ❌ **Vendor lock-in** - proprietary platform
- ❌ **Theme limitations** - harder to customize deeply
- ❌ **App dependency** - additional costs for features

#### Ideal Use Cases
- Standard e-commerce stores
- Businesses wanting proven reliability
- Teams needing full-featured commerce platform
- Sites requiring extensive app ecosystem

#### Example Configuration
```bash
blackwell init project online-store \
  --cms contentful \
  --ecommerce shopify_basic \
  --ssg gatsby \
  --integration event_driven \
  --budget 400
```

## SSG Engines

### Hugo

**💰 Cost**: **FREE**
**⚡ Build Speed**: **Fastest** (1000+ pages/second)
**🎯 Best For**: Technical teams, performance-critical sites, large content volumes

#### Pros
- ✅ **Extremely fast builds** - Go-powered performance
- ✅ **Minimal resource usage** - low AWS build costs
- ✅ **Mature and stable** - battle-tested platform
- ✅ **Great for blogs** - excellent content management features

#### Cons
- ❌ **Technical learning curve** - Go templates, limited JavaScript
- ❌ **Less modern tooling** - fewer contemporary web features
- ❌ **Configuration complexity** - YAML/TOML configuration

#### Best CMS Pairings
- **Decap**: Perfect for technical blogs
- **Contentful**: Good for high-volume content sites

---

### Eleventy

**💰 Cost**: **FREE**
**⚡ Build Speed**: **Very Fast**
**🎯 Best For**: Balanced approach, flexible templating, business websites

#### Pros
- ✅ **Multiple template languages** - Nunjucks, Liquid, Handlebars
- ✅ **JavaScript ecosystem** - modern tooling available
- ✅ **Fast builds** - excellent performance
- ✅ **Incremental adoption** - easy migration from other SSGs

#### Cons
- ❌ **Configuration can be complex** - many options to learn
- ❌ **Smaller community** - fewer themes and plugins

#### Best CMS Pairings
- **Decap**: Great for business websites
- **Sanity**: Good for structured content sites

---

### Astro

**💰 Cost**: **FREE**
**⚡ Build Speed**: **Fast**
**🎯 Best For**: Modern sites, component islands, performance-focused development

#### Pros
- ✅ **Component islands** - partial hydration for performance
- ✅ **Framework agnostic** - use React, Vue, Svelte together
- ✅ **Modern developer experience** - TypeScript, hot reload
- ✅ **Excellent performance** - minimal JavaScript by default

#### Cons
- ❌ **Newer platform** - smaller ecosystem
- ❌ **Component complexity** - requires understanding of islands architecture

#### Best CMS Pairings
- **Sanity**: Excellent for structured content
- **Tina**: Great for visual editing
- **Contentful**: Good for enterprise sites

---

### Gatsby

**💰 Cost**: **FREE**
**⚡ Build Speed**: **Good** (slower for large sites)
**🎯 Best For**: React ecosystem, GraphQL, data-heavy sites

#### Pros
- ✅ **React ecosystem** - leverage React components and libraries
- ✅ **GraphQL data layer** - unified data querying
- ✅ **Plugin ecosystem** - extensive plugin library
- ✅ **Image optimization** - excellent built-in image handling

#### Cons
- ❌ **Slow builds** - can be slow for large sites
- ❌ **Complex configuration** - many concepts to learn
- ❌ **Build complexity** - webpack and GraphQL complexity

#### Best CMS Pairings
- **Contentful**: Native GraphQL integration
- **Sanity**: Good for structured content

---

### Next.js & Nuxt.js

**💰 Cost**: **FREE**
**⚡ Build Speed**: **Good**
**🎯 Best For**: Full-stack applications, enterprise features, modern frameworks

#### Pros
- ✅ **Full-stack capabilities** - API routes, server-side rendering
- ✅ **Modern frameworks** - React (Next.js) or Vue (Nuxt.js)
- ✅ **Excellent developer experience** - hot reload, TypeScript support
- ✅ **Deployment flexibility** - static or server-rendered

#### Cons
- ❌ **More complex** - full-stack concepts required
- ❌ **Larger builds** - more JavaScript in final bundle

#### Best CMS Pairings
- **Sanity**: Excellent integration
- **Contentful**: Great for enterprise sites
- **Tina**: Good for React-based workflows

## Provider Combinations

### Budget-Friendly Combinations

#### Option 1: Ultra Budget ($65/month)
```
CMS: Decap (FREE)
E-commerce: None
SSG: Hugo (fastest builds = lower AWS costs)
Integration: Direct
Monthly Cost: ~$65
```

#### Option 2: Budget Store ($89/month + 2% fees)
```
CMS: Decap (FREE)
E-commerce: Snipcart ($29)
SSG: Eleventy
Integration: Event-Driven
Monthly Cost: ~$89 + 2% of sales
```

### Professional Combinations

#### Option 1: Content-Focused ($158/month + 2% fees)
```
CMS: Sanity ($99)
E-commerce: Snipcart ($29)
SSG: Astro
Integration: Event-Driven
Monthly Cost: ~$158 + 2% of sales
```

#### Option 2: High-Volume Store ($174/month + 1.5% fees)
```
CMS: Sanity ($99)
E-commerce: Foxy ($75)
SSG: Astro
Integration: Event-Driven
Monthly Cost: ~$174 + 1.5% of sales
```

### Enterprise Combinations

#### Option 1: Proven Reliability ($430/month + 2.9% fees)
```
CMS: Contentful ($300)
E-commerce: Shopify Basic ($29)
SSG: Gatsby
Integration: Event-Driven
Monthly Cost: ~$430 + 2.9% of sales
```

#### Option 2: High-Performance Enterprise ($374/month + 1.5% fees)
```
CMS: Contentful ($300)
E-commerce: Foxy ($75)
SSG: Next.js
Integration: Event-Driven
Monthly Cost: ~$374 + 1.5% of sales
```

## Selection Framework

### Step 1: Define Your Requirements

#### Team Characteristics
- **Technical expertise level**: Low/Medium/High
- **Team size**: Solo/Small (2-5)/Medium (6-20)/Large (20+)
- **Content editing comfort**: Git/Visual editing/Enterprise workflows

#### Content Requirements
- **Content complexity**: Simple/Structured/Enterprise
- **Content volume**: Low (<100 pages)/Medium (100-1000)/High (1000+)
- **Multi-language needs**: None/Basic/Advanced
- **Collaboration needs**: Solo/Team/Enterprise

#### E-commerce Requirements
- **Store complexity**: None/Simple/Advanced/Enterprise
- **Product volume**: None/Low (<100)/Medium (100-1000)/High (1000+)
- **Transaction volume**: None/Low (<$10K)/Medium ($10K-100K)/High ($100K+)
- **Special features**: Subscriptions/Complex pricing/Custom checkout

#### Technical Requirements
- **Performance needs**: Standard/High/Critical
- **Customization needs**: Low/Medium/High
- **Integration requirements**: Simple/Advanced/Enterprise

### Step 2: Budget Analysis

Use the CLI's built-in cost calculator:

```bash
# Compare options within budget
blackwell cost compare --budget 150

# Get recommendations for specific requirements
blackwell init project my-site --interactive --budget 200
```

### Step 3: Future-Proofing

Consider your growth path:

- **Start simple**: Decap + direct mode → add e-commerce later
- **Plan for scale**: Event-driven mode for future composition
- **Migration path**: Choose providers with good migration options

## Compatibility Matrix

### CMS + SSG Compatibility

| CMS | Hugo | Eleventy | Astro | Gatsby | Next.js | Nuxt.js |
|-----|------|----------|-------|---------|---------|---------|
| **Decap** | ⭐ Perfect | ⭐ Perfect | ✅ Great | ✅ Great | ✅ Good | ✅ Good |
| **Tina** | ❌ Limited | ✅ Good | ⭐ Perfect | ✅ Great | ⭐ Perfect | ⭐ Perfect |
| **Sanity** | ✅ Good | ✅ Great | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect |
| **Contentful** | ✅ Good | ✅ Great | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect |

### E-commerce + SSG Compatibility

| E-commerce | Hugo | Eleventy | Astro | Gatsby | Next.js | Nuxt.js |
|------------|------|----------|-------|---------|---------|---------|
| **Snipcart** | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect | ✅ Great | ✅ Great |
| **Foxy** | ⭐ Perfect | ⭐ Perfect | ⭐ Perfect | ✅ Great | ✅ Great | ✅ Great |
| **Shopify** | ❌ Limited | ✅ Good | ✅ Great | ✅ Great | ⭐ Perfect | ⭐ Perfect |

### Integration Mode Recommendations

| Provider Combination | Direct Mode | Event-Driven Mode |
|---------------------|-------------|-------------------|
| **CMS Only** | ⭐ Recommended | ✅ Optional |
| **E-commerce Only** | ✅ Good | ✅ Good |
| **CMS + E-commerce** | ❌ Not supported | ⭐ Required |

## Quick Selection Guide

### I need a simple blog/portfolio
```bash
blackwell init project my-blog \
  --template cms-only \
  --cms decap \
  --ssg hugo \
  --budget 65
```

### I need a business website with simple store
```bash
blackwell init project my-business \
  --template budget-startup \
  --cms decap \
  --ecommerce snipcart \
  --budget 100
```

### I need advanced content management
```bash
blackwell init project content-site \
  --cms sanity \
  --ssg astro \
  --integration event_driven \
  --budget 180
```

### I need a full e-commerce platform
```bash
blackwell init project my-store \
  --template enterprise \
  --cms contentful \
  --ecommerce shopify_basic \
  --ssg gatsby \
  --budget 450
```

---

**Need help choosing?** Run `blackwell init project <name> --interactive` for guided provider selection with cost analysis and recommendations! 🚀