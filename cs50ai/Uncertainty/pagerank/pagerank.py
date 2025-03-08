import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability={}
    for link in corpus:
        if link == page or link not in corpus[page]:
            probability[link]=(1-damping_factor)/len(corpus)
        elif corpus[page] == {}:
            probability[link]=1/len(corpus)
        else:
            probability[link]=damping_factor/len(corpus[page])+(1-damping_factor)/len(corpus)
    return probability


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    start_page=random.choice(list(corpus.keys()))
    appearance={}
    probability=transition_model(corpus,start_page,damping_factor)
    for i in range(n):
        next_page=random.choices(list(probability.keys()),list(probability.values()))[0]
        appearance[next_page]=appearance.get(next_page,0)+1
        probability=transition_model(corpus,next_page,damping_factor)
    for page in appearance:
        appearance[page]=appearance[page]/n
    return  appearance


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    appearance={}
    num_pages=len(corpus)
    accuracy=0.001
    extra_appearance=0
    for page in corpus:
        appearance[page]=1/num_pages
    while True:
        flag=0
        # 遍历所有页面，计算新的 PageRank 值
        for page in corpus:
            for i in corpus:
                if len(corpus[i])==0:
                    extra_appearance=damping_factor*appearance[i]/num_pages
            # 初始 PageRank 公式的一部分（考虑随机跳转）
            new_appearance = ((1 - damping_factor) / num_pages  )+extra_appearance

        # 遍历 corpus，找到所有指向 `page` 的网页
            for i in corpus:
                if page in corpus[i]:  
                    # 计算 PageRank 传递贡献部分
                    new_appearance += damping_factor * appearance[i] / len(corpus[i])


            # 判断 PageRank 值是否收敛
            if abs(appearance[page] - new_appearance) > accuracy:
                flag = 1  # 标记还没有收敛

            # 更新 PageRank 值
            appearance[page] = new_appearance  

        # 如果所有页面的 PageRank 值变化都小于 accuracy，就停止迭代
        if flag == 0:
            break
    return appearance


if __name__ == "__main__":
    main()
