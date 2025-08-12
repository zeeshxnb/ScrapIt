// Lightweight i18n + preferences helpers with live updates via a window event

export type AppPreferences = {
  theme?: 'light' | 'dark' | 'auto';
  language?: 'en' | 'es' | 'fr' | 'de';
  timezone?: 'auto' | 'utc' | 'pst' | 'est';
  emailsPerPage?: number;
};

const translations: Record<string, Record<string, string>> = {
  en: {
    'nav.dashboard': 'Dashboard',
    'nav.emails': 'Emails',
    'nav.chat': 'AI Assistant',
    'nav.analytics': 'Analytics',
    'nav.settings': 'Settings',

    'dashboard.title': 'Dashboard',
    'dashboard.subtitle': 'Overview of your email management',
    'dashboard.stats.total': 'Total Emails',
    'dashboard.stats.spam': 'Spam Emails',
    'dashboard.stats.unprocessed': 'Unprocessed',
    'dashboard.stats.categories': 'Categories',
    'dashboard.quickActions': 'Quick Actions',
    'dashboard.noActions': 'No quick actions available',
    'dashboard.noActionsHint': 'Sync your emails to see available actions',

    'emails.title': 'Emails',
    'emails.filters': 'Filters',
    'emails.search.placeholder': 'Search emails by subject, sender, or content...',
    'emails.category': 'Category',
    'emails.label': 'Label',
    'emails.sender': 'Sender',
    'emails.spamFilter': 'Spam Filter',
    'emails.allCategories': 'All Categories',
    'emails.allLabels': 'All Labels',
    'emails.allSenders': 'All Senders',
    'emails.allEmails': 'All Emails',
    'emails.notSpam': 'Not Spam',
    'emails.spamOnly': 'Spam Only',
    'emails.clearFilters': 'Clear Filters',
    'emails.noEmails': 'No emails found',
    'emails.tryAdjust': 'Try adjusting your search or filters',
    'emails.syncToSee': 'Sync your emails to see them here',
    'emails.previous': 'Previous',
    'emails.next': 'Next',

    // Chat
    'chat.title': 'AI Assistant',
    'chat.subtitle': 'Chat with your email management assistant',
    'chat.aiPowered': 'AI Powered',
    'chat.quickActions': 'Quick Actions',
    'chat.welcome': "Hi! I'm your ScrapIt AI assistant. I can help you manage your emails with natural language commands.",
    'chat.suggest.showStats': 'Show me my email statistics',
    'chat.suggest.deleteSpam': 'Delete my spam emails',
    'chat.suggest.classify': 'Classify my unprocessed emails',
    'chat.suggest.findBoss': 'Find emails from my boss',
    'chat.input.placeholder': 'Ask me anything about your emails...',
    'chat.helper': 'I can help you delete spam, classify emails, search your inbox, and more!',

    // Analytics
    'analytics.title': 'Analytics',
    'analytics.subtitle': 'Insights into your email patterns and management',
    'analytics.refresh': 'Refresh Analytics',
    'analytics.lastUpdated': 'Last updated',
    'analytics.range.7d': 'Last 7 days',
    'analytics.range.30d': 'Last 30 days',
    'analytics.range.90d': 'Last 90 days',
    'analytics.range.1y': 'Last year',
    'analytics.range.lifetime': 'Lifetime',
    'analytics.chart.volume': 'Email Volume Over Time',
    'analytics.chart.categories': 'Email Categories',
    'analytics.processing': 'Processing Status',
    'analytics.processed': 'Processed',
    'analytics.unprocessed': 'Unprocessed',
    'analytics.spamDetected': 'Spam Detected',
    'analytics.vsLastPeriod': 'vs last period',
    'analytics.timeInsights': 'Time Insights',
    'analytics.peakHour': 'Peak Email Hour',
    'analytics.busiestDay': 'Busiest Day',
    'analytics.weekendEmails': 'Weekend Emails',
    'analytics.cleanup': 'Cleanup Efficiency',
    'analytics.labelCoverage': 'Label Coverage',
    'analytics.processedRate': 'Processed Rate',
    'analytics.timeSaved': 'Estimated Time Saved',

    // Settings
    'settings.title': 'Settings',
    'settings.subtitle': 'Manage your account and application preferences',
    'settings.accountInfo': 'Account Information',
    'settings.firstName': 'First Name',
    'settings.lastName': 'Last Name',
    'settings.emailAddress': 'Email Address',
    'settings.accountId': 'Account ID',
    'settings.privacy': 'Privacy & Security',
    'settings.dataRetention': 'Data Retention Period',
    'settings.shareAnalytics': 'Share Anonymous Analytics',
    'settings.emailPreview': 'Email Content Preview',
    'settings.appPrefs': 'Application Preferences',
    'settings.theme': 'Theme',
    'settings.language': 'Language',
    'settings.timezone': 'Timezone',
    'settings.emailsPerPage': 'Emails per page',
    'settings.save': 'Save Settings',
    'settings.quickActions': 'Quick Actions',
    'settings.signOut': 'Sign Out',
    'settings.danger': 'Danger Zone',
    'settings.deleteAccount': 'Delete Account',
    'settings.support': 'Support',
    'settings.privacyPolicy': 'Privacy Policy',
    'settings.terms': 'Terms of Service',
  },
  es: {
    'nav.dashboard': 'Panel',
    'nav.emails': 'Correos',
    'nav.chat': 'Asistente IA',
    'nav.analytics': 'Analítica',
    'nav.settings': 'Ajustes',

    'dashboard.title': 'Panel',
    'dashboard.subtitle': 'Resumen de la gestión de tu correo',
    'dashboard.stats.total': 'Correos totales',
    'dashboard.stats.spam': 'Correos spam',
    'dashboard.stats.unprocessed': 'Sin procesar',
    'dashboard.stats.categories': 'Categorías',
    'dashboard.quickActions': 'Acciones rápidas',
    'dashboard.noActions': 'No hay acciones disponibles',
    'dashboard.noActionsHint': 'Sincroniza tus correos para ver acciones',

    'emails.title': 'Correos',
    'emails.filters': 'Filtros',
    'emails.search.placeholder': 'Busca por asunto, remitente o contenido...',
    'emails.category': 'Categoría',
    'emails.label': 'Etiqueta',
    'emails.sender': 'Remitente',
    'emails.spamFilter': 'Filtro de spam',
    'emails.allCategories': 'Todas las categorías',
    'emails.allLabels': 'Todas las etiquetas',
    'emails.allSenders': 'Todos los remitentes',
    'emails.allEmails': 'Todos los correos',
    'emails.notSpam': 'Sin spam',
    'emails.spamOnly': 'Solo spam',
    'emails.clearFilters': 'Borrar filtros',
    'emails.noEmails': 'No se encontraron correos',
    'emails.tryAdjust': 'Prueba a ajustar tu búsqueda o filtros',
    'emails.syncToSee': 'Sincroniza tus correos para verlos aquí',
    'emails.previous': 'Anterior',
    'emails.next': 'Siguiente',

    'chat.title': 'Asistente IA',
    'chat.subtitle': 'Chatea con tu asistente de correo',
    'chat.aiPowered': 'Con IA',
    'chat.quickActions': 'Acciones rápidas',
    'chat.welcome': '¡Hola! Soy tu asistente de ScrapIt. Puedo ayudarte a gestionar tus correos con lenguaje natural.',
    'chat.suggest.showStats': 'Muéstrame mis estadísticas de correo',
    'chat.suggest.deleteSpam': 'Elimina mis correos spam',
    'chat.suggest.classify': 'Clasifica mis correos sin procesar',
    'chat.suggest.findBoss': 'Encuentra correos de mi jefe',
    'chat.input.placeholder': 'Pregunta lo que quieras sobre tus correos...',
    'chat.helper': 'Puedo ayudarte a eliminar spam, clasificar correos, buscar en tu bandeja y más.',

    'analytics.title': 'Analítica',
    'analytics.subtitle': 'Información sobre tus patrones de correo',
    'analytics.refresh': 'Actualizar analítica',
    'analytics.lastUpdated': 'Última actualización',
    'analytics.range.7d': 'Últimos 7 días',
    'analytics.range.30d': 'Últimos 30 días',
    'analytics.range.90d': 'Últimos 90 días',
    'analytics.range.1y': 'Último año',
    'analytics.range.lifetime': 'Toda la vida',
    'analytics.chart.volume': 'Volumen de correos en el tiempo',
    'analytics.chart.categories': 'Categorías de correo',
    'analytics.processing': 'Estado de procesamiento',
    'analytics.processed': 'Procesados',
    'analytics.unprocessed': 'Sin procesar',
    'analytics.spamDetected': 'Spam detectado',
    'analytics.vsLastPeriod': 'vs periodo anterior',
    'analytics.timeInsights': 'Información temporal',
    'analytics.peakHour': 'Hora pico',
    'analytics.busiestDay': 'Día más activo',
    'analytics.weekendEmails': 'Correos en fin de semana',
    'analytics.cleanup': 'Eficiencia de limpieza',
    'analytics.labelCoverage': 'Cobertura de etiquetas',
    'analytics.processedRate': 'Tasa procesado',
    'analytics.timeSaved': 'Tiempo estimado ahorrado',

    'settings.title': 'Ajustes',
    'settings.subtitle': 'Gestiona tu cuenta y preferencias',
    'settings.accountInfo': 'Información de la cuenta',
    'settings.firstName': 'Nombre',
    'settings.lastName': 'Apellido',
    'settings.emailAddress': 'Correo electrónico',
    'settings.accountId': 'ID de cuenta',
    'settings.privacy': 'Privacidad y seguridad',
    'settings.dataRetention': 'Periodo de retención de datos',
    'settings.shareAnalytics': 'Compartir analíticas anónimas',
    'settings.emailPreview': 'Vista previa de contenido de correo',
    'settings.appPrefs': 'Preferencias de la aplicación',
    'settings.theme': 'Tema',
    'settings.language': 'Idioma',
    'settings.timezone': 'Zona horaria',
    'settings.emailsPerPage': 'Correos por página',
    'settings.save': 'Guardar ajustes',
    'settings.quickActions': 'Acciones rápidas',
    'settings.signOut': 'Cerrar sesión',
    'settings.danger': 'Zona de peligro',
    'settings.deleteAccount': 'Eliminar cuenta',
    'settings.support': 'Soporte',
    'settings.privacyPolicy': 'Política de privacidad',
    'settings.terms': 'Términos del servicio',
  },
  fr: {
    'nav.dashboard': 'Tableau de bord',
    'nav.emails': 'Emails',
    'nav.chat': 'Assistant IA',
    'nav.analytics': 'Analytique',
    'nav.settings': 'Paramètres',

    'dashboard.title': 'Tableau de bord',
    'dashboard.subtitle': 'Aperçu de la gestion de vos emails',
    'dashboard.stats.total': 'Emails totaux',
    'dashboard.stats.spam': 'Emails indésirables',
    'dashboard.stats.unprocessed': 'Non traités',
    'dashboard.stats.categories': 'Catégories',
    'dashboard.quickActions': 'Actions rapides',
    'dashboard.noActions': 'Aucune action disponible',
    'dashboard.noActionsHint': 'Synchronisez vos emails pour voir des actions',

    'emails.title': 'Emails',
    'emails.filters': 'Filtres',
    'emails.search.placeholder': 'Rechercher par objet, expéditeur ou contenu...',
    'emails.category': 'Catégorie',
    'emails.label': 'Libellé',
    'emails.sender': 'Expéditeur',
    'emails.spamFilter': 'Filtre spam',
    'emails.allCategories': 'Toutes les catégories',
    'emails.allLabels': 'Tous les libellés',
    'emails.allSenders': 'Tous les expéditeurs',
    'emails.allEmails': 'Tous les emails',
    'emails.notSpam': 'Sans spam',
    'emails.spamOnly': 'Spam uniquement',
    'emails.clearFilters': 'Effacer les filtres',
    'emails.noEmails': 'Aucun email trouvé',
    'emails.tryAdjust': 'Essayez d’ajuster votre recherche ou vos filtres',
    'emails.syncToSee': 'Synchronisez vos emails pour les voir ici',
    'emails.previous': 'Précédent',
    'emails.next': 'Suivant',

    'chat.title': 'Assistant IA',
    'chat.subtitle': 'Discutez avec votre assistant de messagerie',
    'chat.aiPowered': 'Propulsé par IA',
    'chat.quickActions': 'Actions rapides',
    'chat.welcome': "Bonjour ! Je suis votre assistant ScrapIt. Je peux vous aider à gérer vos emails.",
    'chat.suggest.showStats': 'Afficher mes statistiques d’email',
    'chat.suggest.deleteSpam': 'Supprimer mes spams',
    'chat.suggest.classify': 'Classer mes emails non traités',
    'chat.suggest.findBoss': 'Trouver les emails de mon patron',
    'chat.input.placeholder': 'Demandez-moi n’importe quoi sur vos emails…',
    'chat.helper': 'Je peux supprimer le spam, classer, rechercher et plus encore.',

    'analytics.title': 'Analytique',
    'analytics.subtitle': 'Aperçus de vos habitudes d’email',
    'analytics.refresh': 'Actualiser',
    'analytics.lastUpdated': 'Dernière mise à jour',
    'analytics.range.7d': '7 derniers jours',
    'analytics.range.30d': '30 derniers jours',
    'analytics.range.90d': '90 derniers jours',
    'analytics.range.1y': 'Dernière année',
    'analytics.range.lifetime': 'Durée de vie',
    'analytics.chart.volume': 'Volume de mails dans le temps',
    'analytics.chart.categories': 'Catégories d’emails',
    'analytics.processing': 'Statut de traitement',
    'analytics.processed': 'Traités',
    'analytics.unprocessed': 'Non traités',
    'analytics.spamDetected': 'Spam détecté',
    'analytics.vsLastPeriod': 'vs période précédente',
    'analytics.timeInsights': 'Aperçus temporels',
    'analytics.peakHour': 'Heure de pointe',
    'analytics.busiestDay': 'Jour le plus chargé',
    'analytics.weekendEmails': 'Emails le weekend',
    'analytics.cleanup': 'Efficacité du nettoyage',
    'analytics.labelCoverage': 'Couverture des libellés',
    'analytics.processedRate': 'Taux traité',
    'analytics.timeSaved': 'Temps estimé gagné',

    'settings.title': 'Paramètres',
    'settings.subtitle': 'Gérez votre compte et vos préférences',
    'settings.accountInfo': 'Informations du compte',
    'settings.firstName': 'Prénom',
    'settings.lastName': 'Nom',
    'settings.emailAddress': 'Adresse e-mail',
    'settings.accountId': 'ID du compte',
    'settings.privacy': 'Confidentialité et sécurité',
    'settings.dataRetention': 'Durée de conservation des données',
    'settings.shareAnalytics': 'Partager des analyses anonymes',
    'settings.emailPreview': 'Aperçu du contenu des emails',
    'settings.appPrefs': 'Préférences de l’application',
    'settings.theme': 'Thème',
    'settings.language': 'Langue',
    'settings.timezone': 'Fuseau horaire',
    'settings.emailsPerPage': 'Emails par page',
    'settings.save': 'Enregistrer',
    'settings.quickActions': 'Actions rapides',
    'settings.signOut': 'Se déconnecter',
    'settings.danger': 'Zone de danger',
    'settings.deleteAccount': 'Supprimer le compte',
    'settings.support': 'Support',
    'settings.privacyPolicy': 'Politique de confidentialité',
    'settings.terms': 'Conditions d’utilisation',
  },
  de: {
    'nav.dashboard': 'Übersicht',
    'nav.emails': 'E-Mails',
    'nav.chat': 'KI-Assistent',
    'nav.analytics': 'Analytik',
    'nav.settings': 'Einstellungen',

    'dashboard.title': 'Übersicht',
    'dashboard.subtitle': 'Überblick über Ihr E-Mail-Management',
    'dashboard.stats.total': 'Gesamt-E-Mails',
    'dashboard.stats.spam': 'Spam-E-Mails',
    'dashboard.stats.unprocessed': 'Unbearbeitet',
    'dashboard.stats.categories': 'Kategorien',
    'dashboard.quickActions': 'Schnellaktionen',
    'dashboard.noActions': 'Keine Aktionen verfügbar',
    'dashboard.noActionsHint': 'Synchronisieren Sie E-Mails, um Aktionen zu sehen',

    'emails.title': 'E-Mails',
    'emails.filters': 'Filter',
    'emails.search.placeholder': 'Suche nach Betreff, Absender oder Inhalt...',
    'emails.category': 'Kategorie',
    'emails.label': 'Label',
    'emails.sender': 'Absender',
    'emails.spamFilter': 'Spam-Filter',
    'emails.allCategories': 'Alle Kategorien',
    'emails.allLabels': 'Alle Labels',
    'emails.allSenders': 'Alle Absender',
    'emails.allEmails': 'Alle E-Mails',
    'emails.notSpam': 'Kein Spam',
    'emails.spamOnly': 'Nur Spam',
    'emails.clearFilters': 'Filter löschen',
    'emails.noEmails': 'Keine E-Mails gefunden',
    'emails.tryAdjust': 'Passen Sie Ihre Suche oder Filter an',
    'emails.syncToSee': 'Synchronisieren Sie Ihre E-Mails, um sie hier zu sehen',
    'emails.previous': 'Zurück',
    'emails.next': 'Weiter',

    'chat.title': 'KI-Assistent',
    'chat.subtitle': 'Chatten Sie mit Ihrem E-Mail-Assistenten',
    'chat.aiPowered': 'KI-gestützt',
    'chat.quickActions': 'Schnellaktionen',
    'chat.welcome': 'Hallo! Ich bin Ihr ScrapIt-Assistent. Ich helfe beim E-Mail-Management.',
    'chat.suggest.showStats': 'Zeige mir meine E-Mail-Statistiken',
    'chat.suggest.deleteSpam': 'Lösche meine Spam-E-Mails',
    'chat.suggest.classify': 'Klassifiziere meine unbearbeiteten E-Mails',
    'chat.suggest.findBoss': 'Finde E-Mails meines Chefs',
    'chat.input.placeholder': 'Fragen Sie mich alles zu Ihren E-Mails…',
    'chat.helper': 'Ich kann Spam löschen, klassifizieren, suchen und mehr.',

    'analytics.title': 'Analytik',
    'analytics.subtitle': 'Einblicke in Ihr E-Mail-Verhalten',
    'analytics.refresh': 'Analytik aktualisieren',
    'analytics.lastUpdated': 'Zuletzt aktualisiert',
    'analytics.range.7d': 'Letzte 7 Tage',
    'analytics.range.30d': 'Letzte 30 Tage',
    'analytics.range.90d': 'Letzte 90 Tage',
    'analytics.range.1y': 'Letztes Jahr',
    'analytics.range.lifetime': 'Gesamte Zeit',
    'analytics.chart.volume': 'E-Mail-Volumen über Zeit',
    'analytics.chart.categories': 'E-Mail-Kategorien',
    'analytics.processing': 'Verarbeitungsstatus',
    'analytics.processed': 'Verarbeitet',
    'analytics.unprocessed': 'Unbearbeitet',
    'analytics.spamDetected': 'Spam erkannt',
    'analytics.vsLastPeriod': 'ggü. letzter Periode',
    'analytics.timeInsights': 'Zeiteinblicke',
    'analytics.peakHour': 'Stoßzeit',
    'analytics.busiestDay': 'Stärkster Tag',
    'analytics.weekendEmails': 'E-Mails am Wochenende',
    'analytics.cleanup': 'Aufräum-Effizienz',
    'analytics.labelCoverage': 'Label-Abdeckung',
    'analytics.processedRate': 'Verarbeitungsrate',
    'analytics.timeSaved': 'Ersparte Zeit',

    'settings.title': 'Einstellungen',
    'settings.subtitle': 'Konto und Präferenzen verwalten',
    'settings.accountInfo': 'Kontoinformationen',
    'settings.firstName': 'Vorname',
    'settings.lastName': 'Nachname',
    'settings.emailAddress': 'E-Mail-Adresse',
    'settings.accountId': 'Konto-ID',
    'settings.privacy': 'Datenschutz und Sicherheit',
    'settings.dataRetention': 'Aufbewahrungszeitraum',
    'settings.shareAnalytics': 'Anonyme Analysen teilen',
    'settings.emailPreview': 'E-Mail-Inhaltsvorschau',
    'settings.appPrefs': 'App-Einstellungen',
    'settings.theme': 'Thema',
    'settings.language': 'Sprache',
    'settings.timezone': 'Zeitzone',
    'settings.emailsPerPage': 'E-Mails pro Seite',
    'settings.save': 'Einstellungen speichern',
    'settings.quickActions': 'Schnellaktionen',
    'settings.signOut': 'Abmelden',
    'settings.danger': 'Gefahrenzone',
    'settings.deleteAccount': 'Konto löschen',
    'settings.support': 'Support',
    'settings.privacyPolicy': 'Datenschutzrichtlinie',
    'settings.terms': 'Nutzungsbedingungen',
  }
};

export function getPrefs(): AppPreferences {
  try {
    const raw = localStorage.getItem('app_prefs');
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed.preferences || {};
  } catch {
    return {};
  }
}

export function setPrefs(prefs: AppPreferences) {
  try {
    const raw = localStorage.getItem('app_prefs');
    const parsed = raw ? JSON.parse(raw) : {};
    parsed.preferences = { ...(parsed.preferences || {}), ...prefs };
    localStorage.setItem('app_prefs', JSON.stringify(parsed));
    window.dispatchEvent(new CustomEvent('app:prefs-changed', { detail: parsed.preferences }));
  } catch {}
}

export function onPrefsChange(handler: (prefs: AppPreferences) => void) {
  const listener = (e: Event) => {
    const custom = e as CustomEvent<AppPreferences>;
    handler(custom.detail || getPrefs());
  };
  window.addEventListener('app:prefs-changed', listener as EventListener);
  return () => window.removeEventListener('app:prefs-changed', listener as EventListener);
}

export function t(key: string): string {
  const lang = getPrefs().language || 'en';
  const table = translations[lang] || translations.en;
  return table[key] || translations.en[key] || key;
}

export function resolveTimeZone(pref?: AppPreferences['timezone']): string | undefined {
  if (!pref || pref === 'auto') return undefined;
  if (pref === 'utc') return 'UTC';
  if (pref === 'pst') return 'America/Los_Angeles';
  if (pref === 'est') return 'America/New_York';
  return undefined;
}

export function tzOffsetMinutes(pref?: AppPreferences['timezone']): number | undefined {
  if (!pref || pref === 'auto') return undefined;
  if (pref === 'utc') return 0;
  if (pref === 'pst') return 480;
  if (pref === 'est') return 300;
  return undefined;
}


