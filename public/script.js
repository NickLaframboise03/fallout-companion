// Array of character entries.
// Make sure each `pdf` path matches a file in your /pdf folder.
const characters = [
  { name: 'Vault Dweller',           pdf: 'pdf/vault-dweller.pdf' },
  { name: 'Brotherhood Paladin',     pdf: 'pdf/brotherhood-paladin.pdf' },
  { name: 'Wasteland Scavenger',     pdf: 'pdf/wasteland-scavenger.pdf' },
  { name: 'Ghoul Survivor',          pdf: 'pdf/ghoul-survivor.pdf' },
  // …add more as needed…
];

// Renders the list of character links
function renderCharacterList() {
  const listEl = document.getElementById('character-list');
  characters.forEach(({ name, pdf }) => {
    const li = document.createElement('li');
    const a  = document.createElement('a');

    a.textContent = name;
    a.href        = pdf;
    a.target      = '_blank';   // Open in new tab
    a.rel         = 'noopener'; // Security best practice

    li.appendChild(a);
    listEl.appendChild(li);
  });
}

// Wait for DOM, then render
document.addEventListener('DOMContentLoaded', renderCharacterList);
