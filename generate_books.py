#!/usr/bin/env python3
"""Generate synthetic Indonesian book content (realistic paragraphs/chapters)."""
import random
from pathlib import Path

def generate_indonesian_books(target_mb=500, output_file='examples/books_content.txt'):
    """Generate synthetic Indonesian book chapters."""
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    target_bytes = target_mb * 1024 * 1024
    
    print(f"\n{'='*70}")
    print(f"Indonesian Books Dataset Generator")
    print(f"Target: {target_mb} MB")
    print(f"{'='*70}\n")
    
    # Indonesian book themes & topics
    book_themes = {
        'Sejarah Indonesia': [
            'Kerajaan Srivijaya berkembang menjadi pusat perdagangan maritim terbesar di Asia Tenggara.',
            'Dinasti Majapahit memperluas wilayah kekuasaannya hingga mencakup seluruh nusantara.',
            'Kedatangan bangsa Eropa membawa perubahan signifikan dalam struktur sosial dan ekonomi.',
            'Perjuangan kemerdekaan Indonesia dimulai dengan gerakan nasionalisme di awal abad ke-20.',
            'Proklamasi kemerdekaan pada 17 Agustus 1945 menandai lahirnya negara Indonesia modern.',
            'Perjalanan bangsa Indonesia dipenuhi dengan tantangan untuk mempertahankan persatuan.',
            'Pembentukan Pancasila sebagai dasar negara mencerminkan nilai-nilai universal kemanusiaan.',
            'Orde Lama dan Orde Baru membentuk perkembangan politik Indonesia hingga era reformasi.',
        ],
        'Budaya & Sastra': [
            'Wayang kulit merupakan seni pertunjukan tradisional yang kaya akan nilai filosofis.',
            'Batik Indonesia telah diakui UNESCO sebagai warisan budaya tak benda kemanusiaan.',
            'Tari tradisional dari berbagai daerah mencerminkan kekayaan budaya lokal yang unik.',
            'Sastra Indonesia dari zaman Balai Pustaka hingga era modern menunjukkan perkembangan pesat.',
            'Penulis-penulis Indonesia seperti Pramoedya Ananta Toer memberikan kontribusi besar.',
            'Musik tradisional gamelan menjadi identitas budaya Indonesia yang dikenal dunia.',
            'Cerita rakyat dan legenda daerah menyimpan kebijaksanaan nenek moyang kita.',
            'Seni rupa Indonesia menggabungkan pengaruh tradisional dengan modernitas kontemporer.',
        ],
        'Geografi & Alam': [
            'Kepulauan Indonesia terbentang dari Sabang sampai Merauke melintasi tiga zona waktu.',
            'Gunung Krakatau merupakan salah satu gunung berapi paling aktif di dunia.',
            'Hutan tropis Indonesia menjadi paru-paru dunia dengan keanekaragaman hayati tinggi.',
            'Terumbu karang Indonesia adalah ekosistem laut paling produktif di dunia.',
            'Iklim tropis Indonesia mempengaruhi pola pertanian dan kehidupan masyarakat lokal.',
            'Sungai-sungai besar di Indonesia menjadi sumber air bagi jutaan penduduk.',
            'Pantai Indonesia yang indah menarik jutaan wisatawan dari seluruh dunia setiap tahun.',
            'Biodiversity Indonesia mencakup lebih dari sepuluh persen spesies di dunia.',
        ],
        'Pendidikan & Pengetahuan': [
            'Sistem pendidikan Indonesia terus berkembang untuk menghadapi tantangan era digital.',
            'Penelitian ilmiah di Indonesia berkontribusi pada kemajuan sains dan teknologi dunia.',
            'Universitas-universitas terkemuka Indonesia menghasilkan lulusan berkualitas internasional.',
            'Teknologi pendidikan membuka peluang baru untuk akses pendidikan yang lebih luas.',
            'Kurikulum nasional dirancang untuk mengembangkan kompetensi abad ke-21 bagi peserta didik.',
            'Program beasiswa membantu ribuan pelajar Indonesia melanjutkan pendidikan ke jenjang tinggi.',
            'Literasi digital menjadi kebutuhan penting dalam kehidupan masyarakat modern.',
            'Pengembangan sumber daya manusia melalui pendidikan adalah investasi jangka panjang.',
        ],
        'Ekonomi & Bisnis': [
            'Pertumbuhan ekonomi Indonesia menunjukkan tren positif meskipun menghadapi tantangan global.',
            'Industri manufaktur Indonesia memiliki daya saing yang kuat di pasar ASEAN.',
            'Sektor pariwisata memberikan kontribusi signifikan terhadap pendapatan negara.',
            'Koperasi dan usaha kecil menengah menjadi tulang punggung ekonomi nasional.',
            'Ekspor produk pertanian Indonesia mencapai pasar internasional dengan kualitas premium.',
            'Investasi asing langsung meningkatkan pembangunan infrastruktur dan lapangan kerja.',
            'E-commerce berkembang pesat dan mengubah cara konsumen berbelanja di Indonesia.',
            'Pertumbuhan startup teknologi Indonesia menciptakan ekosistem bisnis yang dinamis.',
        ],
        'Kesehatan & Sosial': [
            'Sistem kesehatan nasional berupaya memberikan akses kesehatan untuk semua masyarakat.',
            'Vaksinasi program pemerintah telah berhasil mengeliminasi berbagai penyakit menular.',
            'Program kesejahteraan sosial mendukung keluarga yang kurang mampu di berbagai daerah.',
            'Pencegahan penyakit kronis melalui gaya hidup sehat menjadi fokus utama kesehatan publik.',
            'Tenaga medis profesional bekerja keras dalam melayani kebutuhan kesehatan masyarakat.',
            'Nutrisi yang baik adalah fondasi bagi pertumbuhan optimal anak-anak Indonesia.',
            'Mental health awareness semakin meningkat di kalangan masyarakat urban.',
            'Olahraga dan aktivitas fisik menjadi bagian penting dari gaya hidup sehat.',
        ],
        'Teknologi & Inovasi': [
            'Perkembangan teknologi informasi mengubah cara manusia berkomunikasi dan bekerja.',
            'Internet of Things membuka peluang baru untuk otomasi dalam berbagai sektor.',
            'Artificial intelligence dan machine learning menjadi fokus penelitian di universitas top.',
            'Cybersecurity semakin penting untuk melindungi data dan privasi pengguna digital.',
            'Blockchain technology memiliki potensi besar dalam transformasi digital ekonomi.',
            'Cloud computing memungkinkan akses data dan aplikasi dari mana saja kapan saja.',
            'Mobile technology telah merevolusi cara masyarakat Indonesia mengakses informasi.',
            'Green technology menjadi kunci dalam menjaga kelestarian lingkungan untuk generasi mendatang.',
        ],
    }
    
    connectors = [
        'Selain itu,', 'Dengan demikian,', 'Akibatnya,', 'Oleh karena itu,', 'Sementara itu,',
        'Kemudian,', 'Sebelumnya,', 'Pada saat yang sama,', 'Lebih lanjut,', 'Bagaimanapun,',
        'Ternyata,', 'Menariknya,', 'Sebagai akibatnya,', 'Memang,', 'Pada akhirnya,'
    ]
    
    enhancements = [
        'yang memberikan dampak positif bagi masyarakat.',
        'yang menciptakan lapangan kerja baru.',
        'yang meningkatkan kualitas hidup masyarakat.',
        'yang mendorong inovasi dan kreativitas.',
        'yang memperkuat persatuan dan kesatuan.',
        'yang membangun masa depan yang lebih baik.',
        'yang mencerminkan semangat kebersamaan.',
        'yang menjadi inspirasi bagi generasi mendatang.',
        'yang bernilai tinggi bagi peradaban manusia.',
        'yang terus berkembang seiring perjalanan waktu.',
    ]
    
    print("[*] Generating Indonesian book chapters...\n")
    
    written_bytes = 0
    para_count = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        while written_bytes < target_bytes:
            # Random theme
            theme = random.choice(list(book_themes.keys()))
            sentences = book_themes[theme]
            
            # Build paragraph (3-5 sentences)
            para_length = random.randint(3, 5)
            para_sentences = random.sample(sentences, min(para_length, len(sentences)))
            
            # Add connectors between sentences
            para_text = para_sentences[0]
            for sent in para_sentences[1:]:
                connector = random.choice(connectors)
                para_text += f" {connector} {sent.lower()}"
            
            # Add enhancement
            enhancement = random.choice(enhancements)
            para_text += f" {enhancement}\n"
            
            # Write paragraph
            f.write(para_text + '\n')
            written_bytes += len(para_text.encode('utf-8')) + 1
            para_count += 1
            
            # Progress
            if para_count % 10000 == 0:
                mb = written_bytes / (1024 * 1024)
                pct = (mb / target_mb) * 100
                print(f"  {para_count:,} paragraphs | {mb:.1f}MB ({pct:.0f}%)")
            
            if written_bytes >= target_bytes:
                break
    
    final_size = output_path.stat().st_size / (1024 * 1024)
    final_paras = para_count
    
    print(f"\n{'='*70}")
    print(f"✅ Indonesian Books Dataset READY")
    print(f"{'='*70}")
    print(f"\n📚 Statistics:")
    print(f"   Paragraphs: {final_paras:,}")
    print(f"   File size: {final_size:.1f} MB")
    print(f"   Output: {output_file}\n")
    
    return output_path

if __name__ == '__main__':
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    output = sys.argv[2] if len(sys.argv) > 2 else 'examples/books_content.txt'
    generate_indonesian_books(target, output)
