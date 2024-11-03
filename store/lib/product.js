import { parse } from 'csv-parse/sync';

const DATA_PATH = "/data";
let db = new Map();

export async function getDb() {
    if (db.size === 0) {
        console.log("reading db");
        const filePath = `${DATA_PATH}/product_catalog_v2.csv`;
        const resp = await fetch(filePath);
        const csv = await resp.text();
        const records = parse(csv, { columns: true });
        console.log(`Loaded ${records.length} records`)
        for (const record of records) {
            db[record.article_id] = record;
        }
    }
    return db;
}

export async function getProductData(productId) {
    const db = await getDb();
    const data = db[productId];
    if (!data) {
        console.log(`${productId} not found`);
        return {};
    }
    return data;
}

export async function getProductName(productId) {
    return await getProductData(productId)["prod_name"];
}

export function getProductImage(productId) {
    return `${DATA_PATH}/product_catalog_images/0${productId}.jpg`;
}

export function formatPrice(priceStr) {
    return `$${Number(priceStr).toFixed(2)}`;
}
