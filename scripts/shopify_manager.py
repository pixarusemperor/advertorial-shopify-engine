#!/usr/bin/env python3
"""
Shopify Manager Script for Advertorial & Product Automation
Connects to Shopify Admin GraphQL API using stored CLI tokens.
"""

import json
import sys
import requests

import os

def get_shopify_session():
    # 1. Check environment variables
    env_token = os.environ.get('SHOPIFY_ACCESS_TOKEN')
    env_domain = os.environ.get('SHOPIFY_STORE_DOMAIN', '1nh26y-p9.myshopify.com')
    if env_token:
        headers = {
            'X-Shopify-Access-Token': env_token,
            'Authorization': f'Bearer {env_token}',
            'Content-Type': 'application/json'
        }
        return env_domain, headers

    # 2. Fallback to local Shopify CLI session file if available
    config_path = os.path.expanduser('~/.config/shopify-cli-kit-nodejs/config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            data = json.load(f)
        session_store = json.loads(data['sessionStore'])
        accounts = session_store.get('accounts.shopify.com', {})
        for _, acc in accounts.items():
            if 'identity' in acc and 'accessToken' in acc['identity']:
                token = acc['identity']['accessToken']
                headers = {
                    'X-Shopify-Access-Token': token,
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                return env_domain, headers

    raise ValueError("No Shopify access token found in environment or local CLI config.")

def graphql_query(query, variables=None):
    shop_domain, headers = get_shopify_session()
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    endpoint = f'https://{shop_domain}/admin/api/2024-07/graphql.json'
    resp = requests.post(endpoint, json=payload, headers=headers)
    if resp.status_code != 200:
        raise Exception(f'GraphQL request failed with HTTP {resp.status_code}: {resp.text}')
    return resp.json()

def update_resilia_product(product_id='gid://shopify/Product/10986884170012'):
    description_html = """
<div class="resilia-product-description" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1a1a1a;">
  <div style="background: #f0f7ff; border-left: 4px solid #2b6cb0; padding: 16px 20px; border-radius: 4px; margin-bottom: 24px;">
    <h3 style="margin: 0 0 8px 0; color: #1a365d; font-size: 1.15rem;">🔬 Formule Synergique Cardio-Protectrice Haute Puissance</h3>
    <p style="margin: 0; color: #2d3748; font-size: 0.95rem;">La première association clinique d'<strong>Extrait d'Ail Vieilli 20 Mois</strong> (standardisé en S-allylcystéine SAC) et de <strong>CoQ10 sous forme pure Ubiquinol</strong>, spécialement conçue pour restaurer l'élasticité artérielle, soutenir une tension saine et recharger l'énergie mitochondriale du muscle cardiaque.</p>
  </div>

  <h3 style="color: #2b6cb0; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">Les 4 Piliers d'Action Clinique :</h3>
  <ul style="padding-left: 20px;">
    <li style="margin-bottom: 12px;"><strong>1. Extrait d'Ail Vieilli 20 Mois (600 mg) :</strong> Maturation enzymatique à froid brevetée éliminant l'allicine instable et irritante au profit de la <em>S-allylcystéine (SAC)</em>. 100% inodore, hydrosoluble, hautement assimilable. Stimule la synthèse d'oxyde nitrique pour une vasodilatation saine et durable des artères.</li>
    <li style="margin-bottom: 12px;"><strong>2. Coenzyme Q10 Ubiquinol Actif (100 mg) :</strong> Forme antioxydante active immédiatement utilisable par l'organisme (8x supérieure à l'ubiquinone standard). Elle alimente directement les mitochondries du myocarde en ATP (énergie cellulaire), particulièrement essentielle dès 45 ans ou sous traitement hypolipémiant.</li>
    <li style="margin-bottom: 12px;"><strong>3. Vitamine K2 naturelle (MK-7) :</strong> Régule le métabolisme du calcium pour empêcher les dépôts calciques sur les parois vasculaires et maintenir la souplesse artérielle.</li>
    <li style="margin-bottom: 12px;"><strong>4. Zéro Odeur & Zéro Reflux Gastrique :</strong> Garanti sans haleine persistante, sans brûlure d'estomac ni arrière-goût désagréable.</li>
  </ul>

  <h3 style="color: #2b6cb0; border-bottom: 2px solid #edf2f7; padding-bottom: 8px; margin-top: 24px;">Informations Nutritionnelles & Posologie :</h3>
  <ul style="padding-left: 20px;">
    <li><strong>Conseils d'utilisation :</strong> 2 capsules molles par jour avec un grand verre d'eau, de préférence au cours d'un repas.</li>
    <li><strong>Contenance :</strong> 60 capsules végétales (cure complète de 30 jours).</li>
    <li><strong>Qualité certifiée :</strong> Normes BPF / GMP, sans OGM, sans gluten, sans colorants ni conservateurs artificiels, testé par des laboratoires tiers accrédités.</li>
    <li><strong>Garantie Sérénité :</strong> Garantie Satisfait ou Remboursé de 60 Jours.</li>
  </ul>
</div>
"""
    mutation = """
    mutation UpdateProduct($input: ProductInput!) {
      productUpdate(input: $input) {
        product {
          id
          title
          handle
          status
          variants(first: 5) {
            edges {
              node {
                id
                title
                price
              }
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        'input': {
            'id': product_id,
            'title': 'Resilia® Ail Vieilli Inodore & CoQ10 Ubiquinol (60 Capsules)',
            'handle': 'resilia-ail-vieilli-ubiquinol',
            'descriptionHtml': description_html.strip(),
            'status': 'ACTIVE'
        }
    }
    res = graphql_query(mutation, variables)
    return res

def deploy_theme_advertorial(theme_id='gid://shopify/OnlineStoreTheme/182844915996'):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(base_dir, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    killswitch_css = """
<style id="scoped-advertorial-killswitch">
  /* HARD ISOLATION OF EDITORIAL ADVERTORIAL */
  #header-group,
  #shopify-section-sections--26006241247516__header_section,
  #shopify-section-sections--26006241247516__header_announcements_9jGBFp,
  .shopify-section-group-header-group,
  .shopify-section-group-footer-group,
  footer:not(.article-footer),
  #footer-group,
  .footer-group,
  #chat-drawer,
  .chat-drawer,
  theme-drawer,
  .theme-drawer,
  skip-to-content-link,
  .skip-to-content-link,
  .quick-add-drawer {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    max-height: 0 !important;
    overflow: hidden !important;
    z-index: -9999 !important;
  }

  /* HARD SUPPRESSION OF EASYSELL & COD STICKY WIDGETS */
  #es-popup-button,
  #es-popup-button-product,
  #es-popup-button-cart,
  #es-popup-button-drawer,
  #es-form-button,
  #es-submit-form-button,
  #es-not-eligible-modal,
  #es-popup-upsell-container,
  #easysell-modal,
  #easysell,
  #easysell-upsell,
  .es-sticky,
  .es-sticky-bottom,
  .es-sticky-desktop,
  .es-sticky-top,
  .es-cta-group,
  .es-button-title,
  .es-button-subtitle,
  .es-button-content,
  .es-css,
  [id^="es-popup"],
  [class*="es-sticky"],
  [class*="easysell"],
  [id*="easysell"],
  .easysell-floating-btn,
  .easysell-sticky-button,
  .easysell-cart-sticky,
  .easysell-btn,
  #easysell-btn,
  .easysell-modal,
  [data-easysell],
  [class*="cod-sticky"],
  [id*="cod-sticky"],
  [class*="floating-buy"],
  [id*="floating-buy"],
  [class*="sticky-add-to-cart"],
  [id*="sticky-add-to-cart"],
  sticky-add-to-cart {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    max-height: 0 !important;
    height: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    top: -99999px !important;
    left: -99999px !important;
    z-index: -9999 !important;
  }
</style>
<script id="scoped-advertorial-pruner">
  (function() {
    function purgeWidgets() {
      var rogueSelectors = [
        '#es-popup-button',
        '#es-popup-button-product',
        '#es-popup-button-cart',
        '#es-popup-button-drawer',
        '.es-sticky',
        '[class*="es-sticky"]',
        '[id^="es-popup"]',
        '[class*="easysell"]',
        '[id*="easysell"]',
        '#header-group',
        'footer:not(.article-footer)',
        '#chat-drawer',
        'theme-drawer',
        '[class*="sticky-add-to-cart"]'
      ];
      rogueSelectors.forEach(function(sel) {
        document.querySelectorAll(sel).forEach(function(el) {
          if (!el.closest('.article-container') && !el.closest('.urgency-banner')) {
            try {
              el.remove();
            } catch(e) {
              el.style.setProperty('display', 'none', 'important');
              el.style.setProperty('visibility', 'hidden', 'important');
              el.style.setProperty('opacity', '0', 'important');
              el.style.setProperty('pointer-events', 'none', 'important');
            }
          }
        });
      });
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', purgeWidgets);
    } else {
      purgeWidgets();
    }
    window.addEventListener('load', purgeWidgets);
    var observer = new MutationObserver(purgeWidgets);
    observer.observe(document.documentElement, { childList: true, subtree: true });
    setTimeout(function() { observer.disconnect(); }, 8000);
  })();
</script>
"""

    schema_str = '\n{% schema %}\n{\n  "name": "Advertorial Resilia",\n  "tag": "section",\n  "class": "section-advertorial",\n  "settings": []\n}\n{% endschema %}\n'
    section_content = killswitch_css + html_content + schema_str

    page_json = json.dumps({
        'sections': {
            'main': {
                'type': 'advertorial-resilia',
                'settings': {}
            }
        },
        'order': ['main']
    }, indent=2)

    files = [
        {
            'filename': 'sections/advertorial-resilia.liquid',
            'body': {
                'type': 'TEXT',
                'value': section_content
            }
        },
        {
            'filename': 'templates/page.advertorial.json',
            'body': {
                'type': 'TEXT',
                'value': page_json
            }
        },
        {
            'filename': 'templates/page.contact.json',
            'body': {
                'type': 'TEXT',
                'value': page_json
            }
        }
    ]

    mutation = """
    mutation ThemeUpsert($themeId: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
      themeFilesUpsert(themeId: $themeId, files: $files) {
        upsertedThemeFiles {
          filename
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        'themeId': theme_id,
        'files': files
    }
    return graphql_query(mutation, variables)

def update_theme_layout(theme_id='gid://shopify/OnlineStoreTheme/182844915996'):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    theme_backup_path = os.path.join(base_dir, 'scripts', 'theme.liquid.base')
    with open(theme_backup_path, 'r') as f:
        c = f.read()

    # 1. Define is_advertorial flag at the very start of <head>
    head_tag = '  <head>'
    head_flag = """  <head>
    {% assign is_advertorial = false %}
    {% if template contains 'advertorial' or page.template_suffix == 'advertorial' or page.handle == 'contact' or page.handle == 'advertorial' or page.handle == 'dossier' or request.path contains '/pages/contact' or request.path contains '/pages/advertorial' or request.path contains '/pages/dossier' %}
      {% assign is_advertorial = true %}
    {% endif %}"""
    if head_tag in c:
        c = c.replace(head_tag, head_flag, 1)

    # 2. Complete suppression of EasySell via contract freeze, head mutation observer, and CSS
    old_cfh = "    {{ content_for_header }}"
    new_cfh = """    {% if is_advertorial %}
      <script>
        // 1. Force EasySell to treat page as collection (which aborts enableSticky immediately)
        window.ES_CURRENT_PAGE = "collection";
        try {
          Object.defineProperty(window, 'ES_CURRENT_PAGE', {
            value: 'collection',
            writable: false,
            configurable: false
          });
        } catch(e) {}

        // 2. Lock EASYSELL_CONFIG so any later script read yields inactive & non-sticky
        const disabledESConfig = {
          active: false,
          sticky: false,
          cpb_button: false,
          apply: "none",
          products: [],
          settings: {
            active: false,
            sticky: false,
            cpb_button: false,
            apply: "none",
            products: [],
            form_type: "popup"
          },
          fields: []
        };
        window.EASYSELL_CONFIG = disabledESConfig;
        window.ES_CONFIG = disabledESConfig;
        try {
          Object.defineProperty(window, 'EASYSELL_CONFIG', {
            value: disabledESConfig,
            writable: false,
            configurable: false
          });
          Object.defineProperty(window, 'ES_CONFIG', {
            value: disabledESConfig,
            writable: false,
            configurable: false
          });
        } catch(e) {}

        // 3. Early document-start MutationObserver to block & remove EasySell scripts and buttons
        (function() {
          const obs = new MutationObserver(function(mutations) {
            for (let i = 0; i < mutations.length; i++) {
              const nodes = mutations[i].addedNodes;
              for (let j = 0; j < nodes.length; j++) {
                const node = nodes[j];
                if (node.nodeType !== 1) continue;
                if (node.tagName === 'SCRIPT' && node.src && node.src.indexOf('easysell') !== -1) {
                  try { node.type = 'text/plain'; node.remove(); } catch(err) {}
                  continue;
                }
                if (node.tagName === 'LINK' && node.href && node.href.indexOf('easysell') !== -1) {
                  try { node.remove(); } catch(err) {}
                  continue;
                }
                if (node.id === 'es-script' || node.id === 'es-custom-js' || node.id === 'es-css') {
                  try { node.remove(); } catch(err) {}
                  continue;
                }
                if (node.id === 'es-popup-button' || (node.id && node.id.indexOf('es-popup') === 0) || (node.id && node.id.indexOf('easysell') !== -1)) {
                  try { node.remove(); } catch(err) {}
                  continue;
                }
                if (node.classList && (node.classList.contains('es-sticky') || node.classList.contains('es-css') || node.classList.contains('es-popup-button'))) {
                  try { node.remove(); } catch(err) {}
                  continue;
                }
              }
            }
          });
          obs.observe(document.documentElement, { childList: true, subtree: true });
        })();
      </script>
      <style id="es-killer-css">
        #es-popup-button,
        #es-popup-button-product,
        #es-popup-button-cart,
        #es-popup-button-drawer,
        #es-form-button,
        #es-submit-form-button,
        #easysell,
        #easysell-modal,
        #easysell-upsell,
        .es-sticky,
        .es-sticky-bottom,
        .es-sticky-desktop,
        .es-sticky-top,
        .es-popup-button,
        .es-css,
        [id^="es-popup"],
        [class*="es-sticky"],
        [class*="easysell"],
        [id*="easysell"] {
          display: none !important;
          visibility: hidden !important;
          opacity: 0 !important;
          pointer-events: none !important;
          max-height: 0 !important;
          height: 0 !important;
          width: 0 !important;
          position: fixed !important;
          top: -9999px !important;
          left: -9999px !important;
          z-index: -99999 !important;
        }
      </style>
      {{ content_for_header }}
    {% else %}
      {{ content_for_header }}
    {% endif %}"""
    if old_cfh in c:
        c = c.replace(old_cfh, new_cfh, 1)

    # Wrap skip-to-content and chat-drawer
    old_top_drawers = """    {% render 'skip-to-content-link', href: '#MainContent', text: 'accessibility.skip_to_text' %}

    {% render 'chat-drawer' %}"""
    new_top_drawers = """    {% unless is_advertorial %}
      {% render 'skip-to-content-link', href: '#MainContent', text: 'accessibility.skip_to_text' %}
      {% render 'chat-drawer' %}
    {% endunless %}"""
    if old_top_drawers in c:
        c = c.replace(old_top_drawers, new_top_drawers, 1)

    # Wrap header-group
    old_header = """      <div id="header-group">
        {% sections 'header-group' %}
      </div>"""
    new_header = """      {% unless is_advertorial %}
      <div id="header-group">
        {% sections 'header-group' %}
      </div>
      {% endunless %}"""
    if old_header in c:
        c = c.replace(old_header, new_header, 1)

    # Wrap footer-group
    old_footer = """      <footer>
        {% sections 'footer-group' %}
      </footer>"""
    new_footer = """      {% unless is_advertorial %}
      <footer>
        {% sections 'footer-group' %}
      </footer>
      {% endunless %}"""
    if old_footer in c:
        c = c.replace(old_footer, new_footer, 1)

    # Wrap bottom drawers and modals
    old_bottom_drawers = """    {% render 'cart-drawer', render_wrapper: true %}
    {% render 'theme-drawer' %}

    {% render 'search-modal' %}

    {% if settings.quick_add or settings.mobile_quick_add %}
      {% render 'quick-add-modal' %}
    {% endif %}"""
    new_bottom_drawers = """    {% unless is_advertorial %}
    {% render 'cart-drawer', render_wrapper: true %}
    {% render 'theme-drawer' %}

    {% render 'search-modal' %}

    {% if settings.quick_add or settings.mobile_quick_add %}
      {% render 'quick-add-modal' %}
    {% endif %}
    {% endunless %}"""
    if old_bottom_drawers in c:
        c = c.replace(old_bottom_drawers, new_bottom_drawers, 1)

    mutation = """
    mutation ThemeUpsert($themeId: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
      themeFilesUpsert(themeId: $themeId, files: $files) {
        upsertedThemeFiles {
          filename
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        'themeId': theme_id,
        'files': [
            {
                'filename': 'layout/theme.liquid',
                'body': {
                    'type': 'TEXT',
                    'value': c
                }
            }
        ]
    }
    return graphql_query(mutation, variables)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy_theme':
        res = deploy_theme_advertorial()
        print(json.dumps(res, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == 'update_layout':
        res = update_theme_layout()
        print(json.dumps(res, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == 'update_contact':
        res = update_contact_template()
        print(json.dumps(res, indent=2))
    else:
        result = update_resilia_product()
        print(json.dumps(result, indent=2))



