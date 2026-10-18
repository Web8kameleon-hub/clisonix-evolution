import asyncio
import random
import logging
import unittest

# Konfigurimi i logimit
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Definimi i nyjeve sipas hierarkisë ushtarake
class Node:
    def __init__(self, node_id, role, parent=None):
        self.node_id = node_id
        self.role = role
        self.parent = parent
        self.children = []
        self.is_active = True

    async def execute_task(self):
        """ Simulon ekzekutimin e një detyre nga nyja """
        await asyncio.sleep(random.uniform(0.01, 0.05))  # Simulon vonesën
        logging.info(f"{self.role} {self.node_id} kreu detyrën dhe u fik.")
        self.is_active = False  # Nyja fiket pas përfundimit të detyrës

    async def send_message(self, message):
        """ Dërgon një mesazh te nyja prind """
        if self.parent:
            logging.info(f"{self.role} {self.node_id} dërgon mesazh te {self.parent.role} {self.parent.node_id}: {message}")
            await self.parent.receive_message(message)

    async def receive_message(self, message):
        """ Merr një mesazh dhe e dërgon te nyja prind """
        logging.info(f"{self.role} {self.node_id} mori mesazh: {message}")
        if self.parent:
            await self.send_message(message)

# Krijimi i rrjetit Mesh sipas kontinenteve
async def build_continental_mesh():
    # Komanda Qendrore
    command_center = Node("Komanda-Qendrore", "HQ")

    # Kontinente
    amerika = Node("Komanda-Amerika", "Kontinent", parent=command_center)
    europa = Node("Komanda-Europa", "Kontinent", parent=command_center)
    azia = Node("Komanda-Azia", "Kontinent", parent=command_center)
    afrika = Node("Komanda-Afrika", "Kontinent", parent=command_center)
    command_center.children.extend([amerika, europa, azia, afrika])

    # Divizionet në secilin kontinent
    divisions = []
    for continent in [amerika, europa, azia, afrika]:
        div = Node(f"Divizion-{continent.node_id}", "Divizion", parent=continent)
        continent.children.append(div)
        divisions.append(div)

    # Brigadat në secilin divizion
    brigades = []
    for div in divisions:
        brig = Node(f"Brigada-{div.node_id}", "Brigadë", parent=div)
        div.children.append(brig)
        brigades.append(brig)

    # Batalionet në secilën brigadë
    battalions = []
    for brig in brigades:
        batt = Node(f"Batalion-{brig.node_id}", "Batalion", parent=brig)
        brig.children.append(batt)
        battalions.append(batt)

    # Kompanitë në secilin batalion
    companies = []
    for batt in battalions:
        comp = Node(f"Kompania-{batt.node_id}", "Kompani", parent=batt)
        batt.children.append(comp)
        companies.append(comp)

    # Togat në secilën kompani
    platoons = []
    for comp in companies:
        pl = Node(f"Toga-{comp.node_id}", "Togë", parent=comp)
        comp.children.append(pl)
        platoons.append(pl)

    # Ushtarët në secilën togë
    soldiers = []
    for pl in platoons:
        soldier = Node(f"Ushtar-{pl.node_id}", "Ushtar", parent=pl)
        pl.children.append(soldier)
        soldiers.append(soldier)

    # Simulimi i detyrave dhe dërgimit të mesazheve
    tasks = [node.execute_task() for node in soldiers]
    await asyncio.gather(*tasks)

    # Korrierët dërgojnë informacionin në rrjet
    message = "Urdhër nga Komanda-Qendrore!"
    await europa.send_message(message)

    return command_center, soldiers

# Testimi i rrjetit Mesh
class TestContinentalMesh(unittest.TestCase):
    def test_mesh_structure(self):
        loop = asyncio.get_event_loop()
        command_center, soldiers = loop.run_until_complete(build_continental_mesh())

        # Kontrollo që Komanda Qendrore ka 4 kontinente
        self.assertEqual(len(command_center.children), 4)

        # Kontrollo që secili kontinent ka një divizion
        for continent in command_center.children:
            self.assertEqual(len(continent.children), 1)

        # Kontrollo që secili divizion ka një brigadë
        for continent in command_center.children:
            div = continent.children[0]
            self.assertEqual(len(div.children), 1)

        # Kontrollo që secila brigadë ka një batalion
        for continent in command_center.children:
            div = continent.children[0]
            brig = div.children[0]
            self.assertEqual(len(brig.children), 1)

        # Kontrollo që secili batalion ka një kompani
        for continent in command_center.children:
            div = continent.children[0]
            brig = div.children[0]
            batt = brig.children[0]
            self.assertEqual(len(batt.children), 1)

        # Kontrollo që secila kompani ka një togë
        for continent in command_center.children:
            div = continent.children[0]
            brig = div.children[0]
            batt = brig.children[0]
            comp = batt.children[0]
            self.assertEqual(len(comp.children), 1)

        # Kontrollo që secila togë ka një ushtar
        for continent in command_center.children:
            div = continent.children[0]
            brig = div.children[0]
            batt = brig.children[0]
            comp = batt.children[0]
            pl = comp.children[0]
            self.assertEqual(len(pl.children), 1)

        # Kontrollo që të gjithë ushtarët janë fikur pas përfundimit të detyrës
        for soldier in soldiers:
            self.assertFalse(soldier.is_active)

if __name__ == "__main__":
    unittest.main()
