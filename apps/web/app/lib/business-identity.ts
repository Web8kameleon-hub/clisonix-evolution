export const BUSINESS_IDENTITY = {
  brandName: "Clisonix",
  legalName: "ABA GmbH",
  registrationNumber: "HRB 21069 (Amtsgericht Bochum)",
  taxId: "Available on invoice upon request",
  supportEmail: "clisonix@pm.me",
  privacyEmail: "clisonix@pm.me",
  legalEmail: "clisonix@pm.me",
  supportPhone: "+49 171 3031616",
  address: {
    street: "Wattencheider Hellweg 199",
    city: "Bochum",
    postalCode: "44867",
    region: "NRW",
    country: "Germany",
  },
  domain: "https://www.clisonix.com",
  socialProfiles: [
    {
      name: "GitHub",
      url: "https://github.com/Web8kameleon-hub/clisonix.com",
    },
    {
      name: "LinkedIn",
      url: "https://www.linkedin.com/company/clisonix",
    },
    {
      name: "X",
      url: "https://x.com/clisonix",
    },
  ],
  buyerProtection: [
    "Stripe card payments with dispute handling",
    "PayPal Buyer Protection where PayPal is used",
    "SEPA bank transfer support for approved plans",
  ],
} as const;

export function formatBusinessAddress(): string {
  const { street, city, postalCode, region, country } = BUSINESS_IDENTITY.address;
  return `${street}, ${postalCode} ${city}, ${region}, ${country}`;
}

