// scripts/utt/generate-qr.ts
// Usage: npx tsx scripts/utt/generate-qr.ts ALB-0001 SERIAL-0001 <WALLET_ADDRESS>
import fs from "node:fs";
import path from "node:path";
import qrcode from "qrcode";

async function main() {
  const [tokenId, serial, wallet] = process.argv.slice(2);
  if (!tokenId || !serial || !wallet) {
    console.error("Usage: npx tsx scripts/utt/generate-qr.ts <TOKEN_ID> <SERIAL> <SOL_WALLET>");
    console.error("Example: npx tsx scripts/utt/generate-qr.ts ALB-0001 S-0001 HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU");
    process.exit(1);
  }

  const mint = process.env.ALB_MINT_ADDRESS!;
  if (!mint) {
    console.error("Error: ALB_MINT_ADDRESS not found in environment");
    process.exit(1);
  }

  const data = { 
    tokenId, 
    serial, 
    mint, 
    wallet,
    timestamp: new Date().toISOString(),
    type: 'utt_physical_token'
  };

  // Create Solana URI scheme for wallets
  const uri = `solana:${wallet}?mint=${mint}&ref=${encodeURIComponent(tokenId)}&serial=${encodeURIComponent(serial)}`;
  
  // Create QR data with both URI and metadata
  const qrData = {
    uri,
    data,
    verify_url: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/utt/verify-physical`
  };

  const outDir = path.join(process.cwd(), "public", "utt", "qr");
  fs.mkdirSync(outDir, { recursive: true });
  
  const filename = `${tokenId}-${serial}.png`;
  const filepath = path.join(outDir, filename);
  
  // Generate QR code with high error correction for physical tokens
  await qrcode.toFile(filepath, JSON.stringify(qrData), { 
    margin: 2, 
    width: 512,
    errorCorrectionLevel: 'H', // High error correction for physical wear
    color: {
      dark: '#000000',
      light: '#FFFFFF'
    }
  });

  // Also create a JSON metadata file
  const metaPath = path.join(outDir, `${tokenId}-${serial}.json`);
  fs.writeFileSync(metaPath, JSON.stringify(data, null, 2));

  console.log("✅ QR Code generated successfully:");
  console.log("📄 Image:", filepath);
  console.log("📄 Metadata:", metaPath);
  console.log("🔗 Token ID:", tokenId);
  console.log("🔢 Serial:", serial);
  console.log("💰 Mint:", mint);
  console.log("👤 Wallet:", wallet);
  console.log("📱 URI:", uri);
}

main().catch(e => { 
  console.error("❌ Error generating QR code:", e.message); 
  process.exit(1); 
});
