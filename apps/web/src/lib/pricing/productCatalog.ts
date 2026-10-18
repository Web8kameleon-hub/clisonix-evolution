export interface ProductPlan {
  name: string;
  priceEur: string;
  cadence: 'Per day' | 'Per month';
  status: 'Active' | 'Inactive';
  taxCode: string;
  updatedAt: string;
  createdAt: string;
  category: string;
}

export const PRODUCT_CATALOG: ProductPlan[] = [
  {
    name: 'Clisonix Mesh – 1-Day Unlimited Access',
    priceEur: '€1.00',
    cadence: 'Per day',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'Jul 13, 2026, 6:54 PM',
    createdAt: 'Jul 13, 2026, 6:54 PM',
    category: 'General - Electronically Supplied Services',
  },
  {
    name: 'ultra.clisonix.com acses',
    priceEur: '€59.00',
    cadence: 'Per month',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'May 1, 2026, 8:51 PM',
    createdAt: 'May 1, 2026, 8:51 PM',
    category: 'General - Electronically Supplied Services',
  },
  {
    name: 'SDK clisonix interprise',
    priceEur: '€99.00',
    cadence: 'Per month',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'May 1, 2026, 8:50 PM',
    createdAt: 'May 1, 2026, 8:50 PM',
    category: 'General - Electronically Supplied Services',
  },
  {
    name: 'clisonix basis',
    priceEur: '€29.00',
    cadence: 'Per month',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'May 1, 2026, 8:48 PM',
    createdAt: 'May 1, 2026, 8:48 PM',
    category: 'General - Electronically Supplied Services',
  },
  {
    name: 'clisonix-blog',
    priceEur: '€10.00',
    cadence: 'Per month',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'May 1, 2026, 8:47 PM',
    createdAt: 'May 1, 2026, 8:47 PM',
    category: 'General - Electronically Supplied Services',
  },
  {
    name: 'cwy pro',
    priceEur: '€29.00',
    cadence: 'Per month',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'May 1, 2026, 8:45 PM',
    createdAt: 'May 1, 2026, 8:45 PM',
    category: 'General - Electronically Supplied Services',
  },
  {
    name: 'cwy interprise',
    priceEur: '€99.00',
    cadence: 'Per month',
    status: 'Active',
    taxCode: 'txcd_10000000',
    updatedAt: 'May 1, 2026, 8:44 PM',
    createdAt: 'May 1, 2026, 8:44 PM',
    category: 'General - Electronically Supplied Services',
  },
];

export const HOMEPAGE_TRUTH_STATEMENT =
  'Truth statement: Clisonix homepage, landing, and app now show the same live product catalog naming, pricing cadence, and plan status. No synthetic pricing tiers are presented as real plans.';

export const CLISONIX_COPY_KIT = {
  websiteHeadline: 'Create, research, analyze, automate, and deliver from one adaptive workspace.',
  landingHeadline: 'Connect your accounts once. Ask once. Get real execution with approvals and evidence.',
  appHeadline: 'Goal → Capability → Permission → Execution → Evidence → Artifact',
};
